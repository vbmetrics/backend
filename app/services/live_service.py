# app/services/live_service.py
from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import desc
from sqlmodel import Session, select

from app.crud.crud_action import CRUDAction
from app.crud.crud_match import CRUDMatch
from app.crud.crud_rally import CRUDRally
from app.crud.crud_set import CRUDSet
from app.crud.crud_set_state import crud_set_state
from app.models.match import Match
from app.models.player_team_history import PlayerTeamHistory
from app.models.rally import Rally
from app.models.set import Set
from app.schemas.lineup import (
    LineupSideDTO,
)
from app.services.errors import BadRequestError, NotFoundError
from app.utils.code_parser import ActionToken, parse_rally

# Jeśli nie masz gotowego DTO, tymczasowy typ (spójny z wcześniejszymi ustaleniami):
# class LineupSideDTO(BaseModel):
#     team_id: UUID
#     positions: dict[str, UUID]  # { "P1": ..., "P2": ..., ..., "P6": ... }
#     libero_id: UUID | None = None

WIN_TARGET_NORMAL = 25
WIN_TARGET_TIEBREAK = 15


class LiveService:
    def __init__(
        self,
        match_crud: CRUDMatch,
        set_crud: CRUDSet,
        rally_crud: CRUDRally,
        action_crud: CRUDAction,
    ):
        self.match_crud = match_crud
        self.set_crud = set_crud
        self.rally_crud = rally_crud
        self.action_crud = action_crud

    # ------------------------ Helpers ------------------------

    def _get_match(self, db: Session, match_id: UUID) -> Match:
        m = self.match_crud.get(db=db, id=match_id)
        if not m:
            raise NotFoundError(
                "Match not found",
                code="MATCH_NOT_FOUND",
                details={"match_id": str(match_id)},
            )
        return m

    def _current_set(
        self, db: Session, match_id: UUID, for_update: bool = False
    ) -> Set | None:
        stmt = (
            select(Set).where(Set.match_id == match_id).order_by(desc(Set.set_number))
        )
        if for_update:
            stmt = stmt.with_for_update()
        return db.exec(stmt).first()

    def _create_set(self, db: Session, *, match_id: UUID, set_number: int) -> Set:
        new_set = Set(
            match_id=match_id,
            set_number=set_number,
            home_team_score=0,
            away_team_score=0,
            winner_team_id=None,
        )
        db.add(new_set)
        db.commit()
        db.refresh(new_set)
        return new_set

    def _is_tiebreak(self, set_number: int) -> bool:
        return set_number >= 5  # dopinasz logikę ligi, na teraz standard

    def _win_target(self, set_number: int) -> int:
        return (
            WIN_TARGET_TIEBREAK if self._is_tiebreak(set_number) else WIN_TARGET_NORMAL
        )

    def _map_team_letter(self, letter: Literal["H", "G"]) -> Literal["home", "away"]:
        return "home" if letter == "H" else "away"

    def _opposite(self, side: Literal["home", "away"]) -> Literal["home", "away"]:
        return "away" if side == "home" else "home"

    def _scoring_side_from_terminal(
        self, terminal_action: ActionToken
    ) -> Literal["home", "away"]:
        """
        Zasada v1:
        - jeśli terminal '#' → punkt dla drużyny terminal_action.team
        - jeśli terminal '-' → punkt dla przeciwnika
        """
        if terminal_action.eval == "#":
            return terminal_action.team
        if terminal_action.eval == "-":
            return self._opposite(terminal_action.team)
        raise BadRequestError(
            "Terminal action must be '#' or '-'", code="NO_TERMINAL_FOUND"
        )

    def _jersey_to_player(
        self, db: Session, *, team_id: UUID, season_id: UUID, jersey: int
    ) -> UUID:
        """
        Mapowanie numer -> player_id po PlayerTeamHistory (dla danego sezonu i teamu).
        Zakładamy, że masz w PTH numer w polu jersey_number.
        """
        stmt = (
            select(PlayerTeamHistory)
            .where(
                PlayerTeamHistory.team_id == team_id,
                PlayerTeamHistory.season_id == season_id,
                PlayerTeamHistory.jersey_number == jersey,
            )
            .order_by(desc(PlayerTeamHistory.start_date))
        )
        pth = db.exec(stmt).first()
        if not pth:
            raise BadRequestError(
                "Unknown jersey number for team/season",
                code="UNKNOWN_PLAYER_NUMBER",
                details={
                    "team_id": str(team_id),
                    "season_id": str(season_id),
                    "jersey": jersey,
                },
            )
        return pth.player_id

    # ------------------------ Public API ------------------------

    def init_lineup(
        self,
        db: Session,
        *,
        match_id: UUID,
        home: LineupSideDTO,
        away: LineupSideDTO,
        starting_server: Literal["home", "away"],
    ) -> dict:
        """
        Tworzy set #1 (jeśli nie istnieje) oraz SetState
        z rotacjami P1..P6 i serwującym.
        """
        m = self._get_match(db, match_id)

        s = self._current_set(db, match_id)
        if not s:
            s = self._create_set(db, match_id=match_id, set_number=1)

        # rotacje z positions (P1..P6) – wymagamy kompletności
        def positions_to_rotation(side: LineupSideDTO) -> list[UUID]:
            order = ["P1", "P2", "P3", "P4", "P5", "P6"]
            missing = [
                p for p in order if p not in side.positions or side.positions[p] is None
            ]
            if missing:
                raise BadRequestError(
                    "Missing lineup positions",
                    code="LINEUP_INCOMPLETE",
                    details={"missing": missing},
                )
            return [side.positions[p] for p in order]  # type: ignore

        rot_home = positions_to_rotation(home)
        rot_away = positions_to_rotation(away)

        serving_team_id = (
            m.home_team_id if starting_server == "home" else m.away_team_id
        )
        # Startujący to P1 – serving_index = 0
        data = dict(
            serving_team_id=serving_team_id,
            serving_index=0,
            rotation_home=rot_home,
            rotation_away=rot_away,
            libero_home_id=home.libero_id,
            libero_away_id=away.libero_id,
        )

        ss = crud_set_state.upsert_for_set(db, set_id=s.id, data=data)  # type: ignore[arg-type]

        return {
            "match_id": str(m.id),
            "set_id": str(s.id),
            "set_number": s.set_number,
            "serving_team_id": str(ss.serving_team_id),
            "serving_index": ss.serving_index,
            "rotation_home": [str(x) for x in ss.rotation_home],
            "rotation_away": [str(x) for x in ss.rotation_away],
            "libero_home_id": str(ss.libero_home_id) if ss.libero_home_id else None,
            "libero_away_id": str(ss.libero_away_id) if ss.libero_away_id else None,
        }

    def add_rally(
        self,
        db: Session,
        *,
        match_id: UUID,
        code: str,
        comment: str | None = None,
    ) -> dict:
        """
        Główna ścieżka zapisu rally:
        - parsuje EBNF (code_parser),
        - ustala zwycięzcę,
        - aktualizuje wynik seta i rotacje (side-out → rotacja zwycięzcy),
        - zapisuje Rally (+ doczepienie Action w razie potrzeby),
        - zwraca aktualny snapshot stanu.
        """
        m = self._get_match(db, match_id)

        # Pobierz lub utwórz bieżący set — FOR UPDATE, żeby uniknąć wyścigów
        s = self._current_set(db, match_id, for_update=True)
        if not s:
            s = self._create_set(db, match_id=match_id, set_number=1)

        ss = crud_set_state.get_by_set_id(db, set_id=s.id, for_update=True)  # type: ignore[arg-type]
        if not ss:
            raise BadRequestError(
                "Set state not initialized. Call /lineup first.",
                code="SET_STATE_MISSING",
            )

        # 1) Parser
        parsed = parse_rally(code)
        terminal = parsed.actions[parsed.terminal_index]
        scoring_side = self._scoring_side_from_terminal(terminal)  # "home" | "away"

        # 2) Update wyniku
        if scoring_side == "home":
            s.home_team_score += 1
        else:
            s.away_team_score += 1

        # 3) Side-out/rotacje/serwujący na następne rally
        #    Zasada: po każdym rally serwuje zwycięzca następnego.
        #    Jeśli zwycięzca ≠ dotychczas serwujący → side-out
        prev_serving_team_id = ss.serving_team_id
        new_serving_team_id = (
            m.home_team_id if scoring_side == "home" else m.away_team_id
        )
        sideout = prev_serving_team_id != new_serving_team_id

        if sideout:
            # rotacja drużyny, która zdobyła punkt "po przyjęciu"
            if scoring_side == "home":
                ss.rotation_home = (
                    ss.rotation_home[1:] + ss.rotation_home[:1]
                )  # cyklicznie w prawo
            else:
                ss.rotation_away = ss.rotation_away[1:] + ss.rotation_away[:1]
            ss.serving_index = 0  # po side-oucie serwuje P1 nowo serwującej drużyny
        else:
            # bez side-out – serwuje ten sam zawodnik lub (wg Twojej konwencji)
            # kolejny w tej samej drużynie?
            # Najczęstsza konwencja: ten sam serwujący aż do straty.
            # Zostawiamy serving_index bez zmian.
            pass

        ss.serving_team_id = new_serving_team_id

        # 4) Numeracja rally w secie
        rally_no = s.home_team_score + s.away_team_score  # po inkrementacji w (2)

        # 5) Zapis Rally
        serve_team_id_for_this_rally = (
            prev_serving_team_id  # serwujący "przed" tą wymianą
        )
        score_team_id = new_serving_team_id

        r = Rally(
            set_id=s.id,
            rally_number_in_set=rally_no,
            raw_rally_code=code,
            comment=comment,
            serve_team_id=serve_team_id_for_this_rally,
            score_team_id=score_team_id,
        )
        db.add(r)
        db.flush()  # mamy r.id

        # 6) (opcjonalny) zapis akcji — jeśli chcesz szczegółowo Action-y:
        #    mapujemy jersey -> player_id po teamie zwycięzcy/drużynach
        #    Tu minimalnie zapisujemy nic lub tylko terminal – decyzja domenowa.
        #    Zostawiam szkic do rozszerzenia:
        # for atok in parsed.actions:
        #     # wybór team_id tej akcji:
        #     team_id = m.home_team_id if atok.team == "home" else m.away_team_id
        #     player_id = self._jersey_to_player(db, team_id=team_id,
        # season_id=m.season_id, jersey=atok.player_jersey)
        #     act = Action(
        #         rally_id=r.id,
        #         team_id=team_id,
        #         player_id=player_id,
        #         skill=atok.skill,
        #         eval_mark=atok.eval,
        #         start_zone=f"{atok.start.zone}{atok.start.sub}"
        # if atok.start else None,
        #         end_zone=f"{atok.end.zone}{atok.end.sub}" if atok.end else None,
        #         modifiers=atok.modifiers,
        #         seq=atok.index,
        #     )
        #     db.add(act)

        # 7) Zakończenie seta/meczu
        target = self._win_target(s.set_number)

        def won_set(home: int, away: int, tgt: int) -> str | None:
            if home >= tgt or away >= tgt:
                if abs(home - away) >= 2 and (home >= tgt or away >= tgt):
                    return "home" if home > away else "away"
            return None

        winner_side = won_set(s.home_team_score, s.away_team_score, target)
        if winner_side:
            s.winner_team_id = (
                m.home_team_id if winner_side == "home" else m.away_team_id
            )

            # policz wygrane sety w meczu
            # (jeśli chcesz od razu zamykać mecz i ustawiać winner_team_id meczu)
            stmt_sets = select(Set).where(Set.match_id == m.id)
            all_sets = list(db.exec(stmt_sets))
            home_sets = sum(1 for x in all_sets if x.winner_team_id == m.home_team_id)
            away_sets = sum(1 for x in all_sets if x.winner_team_id == m.away_team_id)

            # prosty wariant: best-of-5 (do 3 wygranych)
            if home_sets >= 3 or away_sets >= 3:
                m.winner_team_id = (
                    m.home_team_id if home_sets > away_sets else m.away_team_id
                )
            else:
                # utwórz następny set ze stanem "czystym"
                next_set = self._create_set(
                    db, match_id=m.id, set_number=s.set_number + 1
                )
                # domyślnie serwujący w nowym secie – wg przepisów: na zmianę,
                # tutaj prosto: zwycięzca poprzedniego seta zaczyna (możesz zmienić)
                ss_next_data = dict(
                    serving_team_id=s.winner_team_id,
                    serving_index=0,
                    rotation_home=ss.rotation_home,
                    rotation_away=ss.rotation_away,
                    libero_home_id=ss.libero_home_id,
                    libero_away_id=ss.libero_away_id,
                )
                crud_set_state.upsert_for_set(db, set_id=next_set.id, data=ss_next_data)  # type: ignore[arg-type]

        # 8) Commit
        db.add(s)
        db.add(ss)
        db.add(m)
        db.commit()
        db.refresh(s)
        db.refresh(ss)

        return self.get_state(db, match_id=match_id)

    def get_state(self, db: Session, *, match_id: UUID) -> dict:
        """
        Zwraca snapshot bieżącego seta i stanu (rotacje, serwujący, wynik)
        + ostatnie 10 rally (raw + id).
        """
        m = self._get_match(db, match_id)
        s = self._current_set(db, match_id)
        if not s:
            return {
                "match_id": str(m.id),
                "current_set": None,
                "home_sets": 0,
                "away_sets": 0,
                "home_points": 0,
                "away_points": 0,
                "serving_team_id": None,
                "serving_index": None,
                "rotation_home": [],
                "rotation_away": [],
                "recent_rallies": [],
            }

        ss = crud_set_state.get_by_set_id(db, set_id=s.id)  # type: ignore[arg-type]
        if not ss:
            raise BadRequestError(
                "Set state not initialized. Call /lineup first.",
                code="SET_STATE_MISSING",
            )

        # policz wygrane sety
        stmt_sets = select(Set).where(Set.match_id == m.id)
        all_sets = list(db.exec(stmt_sets))
        home_sets = sum(1 for x in all_sets if x.winner_team_id == m.home_team_id)
        away_sets = sum(1 for x in all_sets if x.winner_team_id == m.away_team_id)

        # ostatnie 10 rally
        stmt_r = (
            select(Rally)
            .where(Rally.set_id == s.id)
            .order_by(desc(Rally.rally_number_in_set))
            .limit(10)
        )
        last = list(db.exec(stmt_r))
        last_out = [
            {
                "id": str(r.id),
                "no": r.rally_number_in_set,
                "code": r.raw_rally_code,
                "serve_team_id": str(r.serve_team_id),
                "score_team_id": str(r.score_team_id),
            }
            for r in reversed(last)  # od najstarszego do najnowszego
        ]

        return {
            "match_id": str(m.id),
            "current_set": {
                "set_id": str(s.id),
                "set_number": s.set_number,
            },
            "home_sets": home_sets,
            "away_sets": away_sets,
            "home_points": s.home_team_score,
            "away_points": s.away_team_score,
            "serving_team_id": str(ss.serving_team_id),
            "serving_index": ss.serving_index,
            "rotation_home": [str(x) for x in ss.rotation_home],
            "rotation_away": [str(x) for x in ss.rotation_away],
            "libero_home_id": str(ss.libero_home_id) if ss.libero_home_id else None,
            "libero_away_id": str(ss.libero_away_id) if ss.libero_away_id else None,
            "recent_rallies": last_out,
        }
