from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlmodel import Session, select

# === ZAŁOŻONE MODELE (proponowane) ===
# Jeśli masz już swoje, podmień importy/nazwy pól.
from app.models.match import Match
from app.models.rally import Rally
from app.models.set import Set
from app.schemas.lineup import LineupCreateDTO, LineupSideDTO
from app.schemas.state import MatchStateDTO, RotationDTO
from app.services.errors import BadRequestError, NotFoundError

Side = Literal["home", "away"]


class MatchFlowService:
    # ---------- mapowanie i snapshot ----------

    def _rotation_from_lineup(self, side: LineupSideDTO) -> RotationDTO:
        # Zakładamy, że kolejność serwisu = P1..P6
        order = [
            side.positions["P1"],
            side.positions["P2"],
            side.positions["P3"],
            side.positions["P4"],
            side.positions["P5"],
            side.positions["P6"],
        ]
        return RotationDTO(order=order, libero_id=side.libero_id)

    def _snapshot(self, match: Match, set_: Set) -> MatchStateDTO:
        return MatchStateDTO(
            match_id=match.id,
            set_number=set_.set_number,
            home_sets=match.home_team_score or 0,
            away_sets=match.away_team_score or 0,
            home_points=set_.home_points,
            away_points=set_.away_points,
            serving_side=set_.serving_side,  # "home" | "away"
            serving_index=set_.serving_index,  # 0..5
            rotation_home=RotationDTO(
                order=set_.rotation_home, libero_id=set_.libero_home_id
            ),
            rotation_away=RotationDTO(
                order=set_.rotation_away, libero_id=set_.libero_away_id
            ),
            last_rallies=[
                {
                    "id": r.id,
                    "code": r.code,
                    "result": r.result_side,
                    "score": r.score_after,
                }
                for r in set_.rallies[-10:]  # relationship, patrz model Rally poniżej
            ],
        )

    # ---------- public API ----------

    def apply_initial_lineup(
        self, *, db: Session, match_id: UUID, dto: LineupCreateDTO
    ) -> MatchStateDTO:
        match = db.get(Match, match_id)
        if not match:
            raise NotFoundError(
                "Match not found",
                code="MATCH_NOT_FOUND",
                details={"match_id": str(match_id)},
            )

        # walidacja spójności
        if (
            dto.home.team_id != match.home_team_id
            or dto.away.team_id != match.away_team_id
        ):
            raise BadRequestError(
                "Lineup teams must match the match participants.",
                code="LINEUP_TEAM_MISMATCH",
            )

        # set# – pobierz lub utwórz
        set_stmt = select(Set).where(
            Set.match_id == match_id, Set.set_number == dto.set_number
        )
        set_ = db.exec(set_stmt).first()
        if set_ and set_.status != "scheduled":
            raise BadRequestError(
                "This set is already live/finished.", code="SET_ALREADY_STARTED"
            )

        if not set_:
            set_ = Set(
                match_id=match_id,
                set_number=dto.set_number,
                home_points=0,
                away_points=0,
                rotation_home=[],
                rotation_away=[],
                libero_home_id=None,
                libero_away_id=None,
                serving_side="home",
                serving_index=0,
                status="scheduled",
                created_at=datetime.utcnow(),
            )
            db.add(set_)
            db.flush()

        rot_home = self._rotation_from_lineup(dto.home)
        rot_away = self._rotation_from_lineup(dto.away)

        set_.rotation_home = rot_home.order
        set_.rotation_away = rot_away.order
        set_.libero_home_id = rot_home.libero_id
        set_.libero_away_id = rot_away.libero_id

        if dto.starting_server_side:
            set_.serving_side = dto.starting_server_side
        if dto.starting_server_index is not None:
            set_.serving_index = dto.starting_server_index

        set_.status = "live"
        db.add(set_)
        db.commit()
        db.refresh(set_)

        return self._snapshot(match, set_)

    def get_state(self, *, db: Session, match_id: UUID) -> MatchStateDTO:
        match = db.get(Match, match_id)
        if not match:
            raise NotFoundError(
                "Match not found",
                code="MATCH_NOT_FOUND",
                details={"match_id": str(match_id)},
            )

        # ostatni live set (albo finished, jeśli live nie ma)
        set_stmt = (
            select(Set).where(Set.match_id == match_id).order_by(Set.set_number.desc())
        )
        set_ = db.exec(set_stmt).first()
        if not set_:
            # brak setów – zwróć „pusty” snapshot, żeby UI wiedziało co robić
            return MatchStateDTO(
                match_id=match.id,
                set_number=1,
                home_sets=match.home_team_score or 0,
                away_sets=match.away_team_score or 0,
                home_points=0,
                away_points=0,
                serving_side="home",
                serving_index=0,
                rotation_home=RotationDTO(order=[], libero_id=None),
                rotation_away=RotationDTO(order=[], libero_id=None),
                last_rallies=[],
            )
        return self._snapshot(match, set_)

    def add_rally_from_code(
        self, *, db: Session, match_id: UUID, code: str
    ) -> MatchStateDTO:
        """
        Placeholder logiki – dopóki nie podepniemy pełnego parsera „kodu akcji”.
        Zasada tymczasowa:
          - jeśli code kończy się na '+' => punkt dla serwującego
          - jeśli kończy się na '-' => punkt dla przeciwnej strony
          - inaczej: treat as error -> punkt dla przeciwnej strony
        Rotacja: jeżeli punkt zdobywa RECEIVING side (side-out), to serwująca zmienia
        się i indeks przesuwa się o 1 w „nowo serwującej” drużynie.
        """

        # TODO

        match = db.get(Match, match_id)
        if not match:
            raise NotFoundError("Match not found", code="MATCH_NOT_FOUND")

        set_stmt = (
            select(Set).where(Set.match_id == match_id).order_by(Set.set_number.desc())
        )
        set_ = db.exec(set_stmt).first()
        if not set_ or set_.status != "live":
            raise BadRequestError("No live set. Set lineup first.", code="SET_NOT_LIVE")

        code = code.strip()
        if not code:
            raise BadRequestError("Code cannot be empty.", code="EMPTY_CODE")

        serving = set_.serving_side  # "home"|"away"
        receiving: Side = "home" if serving == "away" else "away"

        last_char = code[-1]
        if last_char == "+":
            winner: Side = serving
        elif last_char == "-":
            winner = receiving
        else:
            winner = receiving

        # aktualizacja punktów i rotacji
        if winner == "home":
            set_.home_points += 1
        else:
            set_.away_points += 1

        # side-out => zmiana serwującego i rotacja
        if winner == receiving:
            set_.serving_side = receiving
            # rotacja o 1 „do przodu” w drużynie, która będzie serwować
            if receiving == "home":
                set_.serving_index = (set_.serving_index + 1) % 6
            else:
                set_.serving_index = (set_.serving_index + 1) % 6

        # zapisz rally
        # start_score = f"{set_.home_points}:{set_.away_points}"

        # po aktualizacji – wynik końcowy tej wymiany:
        score_after = f"{set_.home_points}:{set_.away_points}"

        rally = Rally(
            match_set_id=set_.id,
            code=code,
            result_side=winner,
            score_after=score_after,
            created_at=datetime.utcnow(),
        )
        db.add(rally)

        db.add(set_)
        db.commit()
        db.refresh(set_)
        return self._snapshot(match, set_)
