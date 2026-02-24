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
from app.models.action import Action
from app.models.match import Match
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.models.rally import Rally
from app.models.set import Set
from app.models.special_event import SpecialEvent
from app.schemas.lineup import (
    LineupSideDTO,
)
from app.services.errors import BadRequestError, NotFoundError
from app.utils.code_parser import (
    ParsedRally,
    parse_rally,
)
from app.utils.special_event_parser import SpecialEventParser, parse_special

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
        db.flush()
        db.refresh(new_set)
        return new_set

    def _is_tiebreak(self, set_number: int) -> bool:
        return set_number >= 5

    def _win_target(self, set_number: int) -> int:
        return (
            WIN_TARGET_TIEBREAK if self._is_tiebreak(set_number) else WIN_TARGET_NORMAL
        )

    def _map_team_letter(self, letter: Literal["H", "G"]) -> Literal["home", "away"]:
        return "home" if letter == "H" else "away"

    def _opposite(self, side: Literal["home", "away"]) -> Literal["home", "away"]:
        return "away" if side == "home" else "home"

    def _jersey_to_player(
        self, db: Session, *, team_id: UUID, season_id: UUID, jersey: int
    ) -> UUID:
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
        m = self._get_match(db, match_id)

        s = self._current_set(db, match_id)
        if not s:
            s = self._create_set(db, match_id=match_id, set_number=1)

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
            return [side.positions[p] for p in order]

        rot_home = positions_to_rotation(home)
        rot_away = positions_to_rotation(away)

        serving_team_id = (
            m.home_team_id if starting_server == "home" else m.away_team_id
        )

        data = dict(
            serving_team_id=serving_team_id,
            serving_index=0,
            rotation_home=[str(u) for u in rot_home],
            rotation_away=[str(u) for u in rot_away],
            libero_home_id=home.libero_id,
            libero_away_id=away.libero_id,
        )

        ss = crud_set_state.upsert_for_set(db, set_id=s.id, data=data)

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
        m = self._get_match(db, match_id)

        s = self._current_set(db, match_id, for_update=True)
        if not s:
            s = self._create_set(db, match_id=match_id, set_number=1)

        ss = crud_set_state.get_by_set_id(db, set_id=s.id, for_update=True)
        if not ss:
            raise BadRequestError(
                "Set state not initialized. Call /lineup first.",
                code="SET_STATE_MISSING",
            )

        if code.startswith("!"):
            special_parsed = parse_special(code)
            return self._handle_special_event(db, m, s, ss, special_parsed, code)

        try:
            parsed: ParsedRally = parse_rally(code)
        except Exception as e:
            if isinstance(e, BadRequestError):
                raise e
            raise BadRequestError(f"Parser error: {str(e)}", code="PARSE_ERROR")

        terminal_action = parsed.actions[parsed.terminal_index]

        scoring_side = None
        if terminal_action.eval == "#":
            scoring_side = terminal_action.team
        elif terminal_action.eval == "-":
            scoring_side = self._opposite(terminal_action.team)
        else:
            raise BadRequestError("Rally must end with a point (#) or error (-)")

        if scoring_side == "home":
            s.home_team_score += 1
        else:
            s.away_team_score += 1

        prev_serving_team_id = ss.serving_team_id
        score_team_id = m.home_team_id if scoring_side == "home" else m.away_team_id

        rally_no = s.home_team_score + s.away_team_score

        new_rally = Rally(
            set_id=s.id,
            rally_number_in_set=rally_no,
            raw_rally_code=code,
            comment=comment or parsed.comment,
            serve_team_id=prev_serving_team_id,
            score_team_id=score_team_id,
            home_score_snapshot=s.home_team_score,
            away_score_snapshot=s.away_team_score
        )
        db.add(new_rally)
        db.flush()

        for action_token in parsed.actions:
            team_id = m.home_team_id if action_token.team == "home" else m.away_team_id
            player_id = None
            try:
                player_id = self._jersey_to_player(
                    db,
                    team_id=team_id,
                    season_id=m.season_id,
                    jersey=action_token.player_jersey
                )
            except BadRequestError:
                pass

            action = Action(
                rally_id=new_rally.id,
                sequence_in_rally=action_token.index + 1,
                raw_action_code=action_token.raw,
                team_context=action_token.team_letter,
                skill_code=action_token.skill,
                evaluation_code=action_token.eval,
                player_jersey_number=action_token.player_jersey,
                player_id=player_id,
                start_zone=int(action_token.start.zone) if action_token.start else None,
                start_subzone=action_token.start.sub if action_token.start else None,
                end_zone=int(action_token.end.zone) if action_token.end else None,
                end_subzone=action_token.end.sub if action_token.end else None,
                modifiers = (
                    "".join(action_token.modifiers) if action_token.modifiers else None
                )
            )
            db.add(action)

        new_serving_team_id = score_team_id
        if prev_serving_team_id != new_serving_team_id:
            if scoring_side == "home":
                ss.rotation_home = ss.rotation_home[1:] + ss.rotation_home[:1]
            else:
                ss.rotation_away = ss.rotation_away[1:] + ss.rotation_away[:1]
            ss.serving_index = 0

        ss.serving_team_id = new_serving_team_id

        # Sprawdzenie końca seta
        if s.winner_team_id is None:
            target = self._win_target(s.set_number)

            def check_set_winner(home, away, tgt):
                if (home >= tgt or away >= tgt) and abs(home - away) >= 2:
                    return "home" if home > away else "away"
                return None

            winner_side = check_set_winner(s.home_team_score, s.away_team_score, target)

            if winner_side:
                s.winner_team_id = (
                    m.home_team_id if winner_side == "home" else m.away_team_id
                )

                stmt_sets = select(Set).where(Set.match_id == m.id, Set.id != s.id)
                past_sets_db = list(db.exec(stmt_sets))

                home_sets_won = sum(
                    1 for x in past_sets_db if x.winner_team_id == m.home_team_id
                )
                away_sets_won = sum(
                    1 for x in past_sets_db if x.winner_team_id == m.away_team_id
                )

                # Dopiero tutaj dodajemy 1 za właśnie wygranego seta
                if winner_side == "home":
                    home_sets_won += 1
                else:
                    away_sets_won += 1

                if home_sets_won == 3 or away_sets_won == 3:
                    m.winner_team_id = (
                        m.home_team_id if home_sets_won > away_sets_won else m.away_team_id # NOQA
                    )
                else:
                    # TWORZYMY NOWY SET
                    next_set_num = s.set_number + 1
                    next_set = self._create_set(
                        db, match_id=m.id, set_number=next_set_num
                    )

                    ss_next_data = {
                        "serving_team_id": str(s.winner_team_id),
                        "serving_index": 0,
                        "rotation_home": ss.rotation_home,
                        "rotation_away": ss.rotation_away,
                        "libero_home_id": ss.libero_home_id,
                        "libero_away_id": ss.libero_away_id
                    }
                    crud_set_state.upsert_for_set(
                        db, set_id=next_set.id, data=ss_next_data
                        )

        db.add(s)
        db.add(ss)
        db.add(m)
        db.commit()
        db.refresh(s)

        return self.get_state(db, match_id=match_id)

    def _handle_special_event(self, db, m, s, ss, parsed, code):
        from app.models.special_event import SpecialEvent, SpecialEventType

        side = "away" if "a" in parsed.raw else "home"
        team_id = m.home_team_id if side == "home" else m.away_team_id

        ev_type = SpecialEventType.other
        if parsed.kind == "T":
            ev_type = SpecialEventType.timeout
        elif parsed.kind == "S":
            ev_type = SpecialEventType.substitution
        elif parsed.kind == "C":
            ev_type = SpecialEventType.card
        elif parsed.kind == "RC":
            ev_type = SpecialEventType.card

        if parsed.kind in ["F", "RC"]:
            scoring_side = self._opposite(side)
            if scoring_side == "home":
                s.home_team_score += 1
            else:
                s.away_team_score += 1

        evt = SpecialEvent(
            event_type=ev_type,
            raw_special_code=code,
            match_id=m.id,
            set_id=s.id,
            team_id=team_id,
            details={"payload": parsed.payload}
        )
        db.add(evt)
        db.add(s)
        db.commit()

        return self.get_state(db, match_id=m.id)

    def get_state(self, db: Session, *, match_id: UUID) -> dict:
        m = self._get_match(db, match_id)

        stmt_sets = select(Set).where(Set.match_id == m.id).order_by(Set.set_number)
        all_sets = list(db.exec(stmt_sets))

        home_sets = sum(1 for x in all_sets if x.winner_team_id == m.home_team_id)
        away_sets = sum(1 for x in all_sets if x.winner_team_id == m.away_team_id)

        s = self._current_set(db, match_id)

        past_sets_out = []
        if s:
            past_sets_out = [
                {
                    "set_number": x.set_number,
                    "home_score": x.home_team_score,
                    "away_score": x.away_team_score
                }
                for x in all_sets if x.id != s.id and x.winner_team_id is not None
            ]

        if not s:
            return {
                "match_id": m.id,
                "set_number": 0,
                "home_sets": home_sets, # Zmieniono na zliczone z bazy
                "away_sets": away_sets,
                "home_points": 0,
                "away_points": 0,
                "serving_side": "home",
                "serving_index": 0,
                "rotation_home": {"order": [], "libero_id": None},
                "rotation_away": {"order": [], "libero_id": None},
                "last_rallies": [],
                "past_sets": past_sets_out
            }

        ss = crud_set_state.get_by_set_id(db, set_id=s.id)

        if not ss:
            return {
                "match_id": m.id,
                "set_number": s.set_number,
                "home_sets": home_sets,
                "away_sets": away_sets,
                "home_points": s.home_team_score,
                "away_points": s.away_team_score,
                "serving_side": "home",
                "serving_index": 0,
                "rotation_home": {"order": [], "libero_id": None},
                "rotation_away": {"order": [], "libero_id": None},
                "last_rallies": [],
                "past_sets": past_sets_out
            }

        # serving_side = "home" if ss.serving_team_id == m.home_team_id else "away"

        serving_team_id = ss.serving_team_id

        # --- NOWA LOGIKA LIBERO ---
        active_player_ids = (ss.rotation_home or []) + (ss.rotation_away or [])
        pos_map = {}
        if active_player_ids:
            try:
                players = db.exec(
                        select(Player).where(Player.id.in_(active_player_ids))
                    ).all()
            except Exception as e:
                print(f"DEBUG Libero - Błąd pobierania pozycji: {e}")
            # POPRAWKA 1: Wymuszamy, by kluczem słownika był zwykły string
            pos_map = {str(p.id): (p.playing_position or "").lower() for p in players}

        def get_on_court(order, libero_id, is_serving):
            if not order:
                return []
            # POPRAWKA 2: Upewniamy się, że modyfikowana lista składa się ze stringów
            on_court = [str(x) for x in order]
            if not libero_id:
                return on_court

            # P1(0), P5(4), P6(5)
            for idx in [0, 4, 5]:
                if idx >= len(on_court):
                    continue

                player_id_str = on_court[idx]
                pos = pos_map.get(player_id_str, "")

                is_mb = "middle" in pos or "mb" in pos or pos == "środkowy"

                if is_mb:
                    if idx == 0 and is_serving:
                        continue
                    on_court[idx] = str(libero_id)
                    break

            return on_court

        on_court_home = get_on_court(
            ss.rotation_home, ss.libero_home_id, serving_team_id == m.home_team_id
        )
        on_court_away = get_on_court(
            ss.rotation_away, ss.libero_away_id, serving_team_id == m.away_team_id
        )
        # ----------------------------------------------------------------

        stmt_r = (
            select(Rally, Set.set_number)
            .join(Set, Rally.set_id == Set.id)
            .where(Set.match_id == m.id)
            .order_by(desc(Set.set_number), desc(Rally.rally_number_in_set))
        )
        last_rallies_db = list(db.exec(stmt_r))

        # 1. Mapujemy standardowe wymiany
        combined_events = [
            {
                "id": r.id,
                "rally_number_in_set": r.rally_number_in_set,
                "set_number": set_num,
                "score_team_id": r.score_team_id,
                "raw_rally_code": r.raw_rally_code,
                "home_score": r.home_score_snapshot,
                "away_score": r.away_score_snapshot,
                "created_at": r.created_at,
                "is_special": False # Flaga pomocnicza
            }
            for r, set_num in last_rallies_db
        ]

        # 2. Pobieramy zdarzenia specjalne
        special_events_db = db.exec(
            select(SpecialEvent, Set.set_number)
            .join(Set, SpecialEvent.set_id == Set.id)
            .where(Set.match_id == m.id)
            .order_by(SpecialEvent.created_at.desc())
            .limit(10)
        ).all()

        for se, set_num in special_events_db:
            combined_events.append({
                "id": se.id,
                "rally_number_in_set": None,
                "set_number": set_num,
                "score_team_id": None,
                "raw_rally_code": se.raw_special_code,
                "home_score": None,
                "away_score": None,
                "created_at": se.created_at,
                "is_special": True # Flaga pomocnicza
            })

        # 3. Sortujemy chronologicznie (NAJSTARSZE na początku)
        combined_events.sort(key=lambda x: (x["created_at"] is None, x["created_at"]))

        # Szukamy pierwszej normalnej wymiany w tym oknie,
        # żeby mieć twardy punkt odniesienia z bazy
        first_db_rally = next((e for e in combined_events if not e["is_special"]), None)

        current_home = first_db_rally["home_score"] if first_db_rally else s.home_team_score  # noqa: E501
        current_away = first_db_rally["away_score"] if first_db_rally else s.away_team_score  # noqa: E501

        # Zaczynamy ciągły licznik od pierwszej pobranej akcji
        # (lub od 1, jeśli dopiero zaczęliśmy seta)
        current_rally_num = first_db_rally["rally_number_in_set"] if first_db_rally and first_db_rally["rally_number_in_set"] else 1  # noqa: E501

        # 4. Przechodzimy przez oś czasu
        for event in combined_events:
            if not event["is_special"]:
                # Aktualizujemy wynik na podstawie twardych danych z bazy
                current_home = event["home_score"]
                current_away = event["away_score"]
            else:
                # Akcje specjalne dziedziczą najświeższy wynik z boiska
                event["home_score"] = current_home
                event["away_score"] = current_away

            # Wymuszamy idealną ciągłość! Każde zdarzenie (wymiana czy kod specjalny)
            # dostaje po prostu kolejny numerek w UI, żeby nie było duplikatów.
            event["rally_number_in_set"] = current_rally_num
            current_rally_num += 1

        # 5. Odwracamy listę z powrotem (NAJNOWSZE na początku) i ucinamy do 10
        combined_events.reverse()
        last_rallies_out = combined_events[:10]

        return {
            "match_id": m.id,
            "set_number": s.set_number,
            "home_sets": home_sets,
            "away_sets": away_sets,
            "home_points": s.home_team_score,
            "away_points": s.away_team_score,
            "serving_side": "home" if serving_team_id == m.home_team_id else "away",
            "serving_index": ss.serving_index,
            "rotation_home": {
                "order": ss.rotation_home,
                "on_court": on_court_home,
                "libero_id": ss.libero_home_id
            },
            "rotation_away": {
                "order": ss.rotation_away,
                "on_court": on_court_away,
                "libero_id": ss.libero_away_id
            },
            "last_rallies": last_rallies_out,
            "past_sets": past_sets_out
        }

    def process_special_event(self, db: Session, match_id: UUID, code: str) -> dict:
        """
        Przetwarza kody specjalne (zaczynające się od '!'),
        zapisuje do bazy i aktualizuje stan seta (wynik/zmiany).
        """
        # 1. Parsowanie kodu nowym parserem
        parsed_event = SpecialEventParser.parse(code)

        # 2. Pobranie aktywnego meczu i seta
        m = self._get_match(db, match_id)
        s = self._current_set(db, match_id)
        if not s:
            raise BadRequestError("Cannot add special event. No active set.")

        # 3. Rozpoznanie, KOGO dotyczy zdarzenie (Przydatne dla kar Sędziego)
        team_id = None
        penalized_team_id = None

        if parsed_event.team == "H":
            team_id = m.home_team_id
            penalized_team_id = m.home_team_id
        elif parsed_event.team == "G":
            team_id = m.away_team_id
            penalized_team_id = m.away_team_id
        elif parsed_event.team == "R":
            # Jeśli to Sędzia (R), sprawdzamy cel (target), np. "H14" lub "G25"
            if parsed_event.target:
                if parsed_event.target.startswith("H"):
                    penalized_team_id = m.home_team_id
                elif parsed_event.target.startswith("G"):
                    penalized_team_id = m.away_team_id

        # 4. KARY PUNKTOWE (Czerwona kartka / Błąd ustawienia)
        if parsed_event.is_penal and penalized_team_id:
            # Jeśli ukarani zostali Gospodarze, punkt dostają Goście (i na odwrót)
            if penalized_team_id == m.home_team_id:
                s.away_team_score += 1
            else:
                s.home_team_score += 1

            # (Uwaga: upewnij się, że wywołujesz tutaj ewentualną logikę końca seta,
            # jeśli ten karny punkt był punktem np. na 25:23)

        # 5. ZMIANY ZAWODNIKÓW (Substitution)
        # Przykład payload/target: "09.23" (zawodnik z nr 9 schodzi, 23 wchodzi)
        if parsed_event.event_type == "S" and parsed_event.target and "." in parsed_event.target:  # noqa: E501
            out_jersey_str, in_jersey_str = parsed_event.target.split(".")

            # Pobieramy ID zawodników na podstawie numerów koszulek i zespołu
            # Wymaga to odpowiedniego zapytania do bazy (np. PlayerTeamHistory)
            # Poniżej pseudokod logiki podmiany w tablicy rotacji:

            """
            out_player_id = self._get_player_id_by_jersey(db, team_id, int(out_jersey_str))
            in_player_id = self._get_player_id_by_jersey(db, team_id, int(in_jersey_str))

            if parsed_event.team == "H" and out_player_id in ss.rotation_home:
                idx = ss.rotation_home.index(out_player_id)
                ss.rotation_home[idx] = in_player_id
                # Wymuszamy na SQLModel zauważenie zmiany w JSON-ie
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(ss, "rotation_home")

            elif parsed_event.team == "G" and out_player_id in ss.rotation_away:
                idx = ss.rotation_away.index(out_player_id)
                ss.rotation_away[idx] = in_player_id
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(ss, "rotation_away")
            """  # noqa: E501

        # 6. Zapis zdarzenia do bazy danych
        # Tworzymy słownik (dict) z detalami
        event_details = {}
        if parsed_event.target:
            event_details["target"] = parsed_event.target
        if parsed_event.comment:
            event_details["comment"] = parsed_event.comment
        if parsed_event.modifier:
            event_details["modifier"] = parsed_event.modifier

        # Tłumaczymy krótkie kody z parsera na pełne słowa dla bazy danych!
        # UWAGA: Podmień wartości po prawej stronie (np. "timeout") na te,
        # które faktycznie istnieją w Twojej klasie SpecialEventType!
        type_mapping = {
            "T": "timeout",
            "S": "substitution",
            "C": "card",
            "F": "fault",
            "RC": "red_card",
            "N": "injury"
        }

        # Pobieramy przetłumaczony typ (lub zostawiamy "unknown", jeśli nie znaleziono)
        mapped_event_type = type_mapping.get(parsed_event.event_type, "timeout")

        db_event = SpecialEvent(
            match_id=m.id,
            set_id=s.id,
            team_id=team_id,
            event_type=mapped_event_type,
            raw_special_code=code,
            details=event_details,
        )

        db.add(db_event)
        db.commit()
        db.refresh(s)

        # 7. Zwracamy zaktualizowany stan
        return self.get_state(db, match_id=match_id)

    def undo_last_rally(self, db: Session, match_id: UUID) -> dict:
        m = self._get_match(db, match_id)
        s = self._current_set(db, match_id, for_update=True)
        if not s:
            raise BadRequestError("No active set")

        ss = crud_set_state.get_by_set_id(db, set_id=s.id, for_update=True)

        stmt = select(
            Rally
        ).where(
            Rally.set_id == s.id
        ).order_by(
            desc(Rally.rally_number_in_set)
        )
        last_rally = db.exec(stmt).first()

        if not last_rally:
            raise BadRequestError(
                "Cannot undo. No rallies in current set.",
                code="UNDO_EMPTY_SET"
            )

        if last_rally.score_team_id == m.home_team_id:
            s.home_team_score -= 1
        else:
            s.away_team_score -= 1

        if last_rally.serve_team_id != last_rally.score_team_id:
            if last_rally.score_team_id == m.home_team_id:
                ss.rotation_home = ss.rotation_home[-1:] + ss.rotation_home[:-1]
            else:
                ss.rotation_away = ss.rotation_away[-1:] + ss.rotation_away[:-1]

        ss.serving_team_id = last_rally.serve_team_id
        ss.serving_index = 0

        s.winner_team_id = None
        m.winner_team_id = None

        from app.models.action import Action
        db.exec(Action.__table__.delete().where(Action.rally_id == last_rally.id))

        db.delete(last_rally)

        db.add(s)
        db.add(ss)
        db.add(m)
        db.commit()

        return self.get_state(db, match_id=match_id)
