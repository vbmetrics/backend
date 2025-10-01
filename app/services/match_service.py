from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_match import CRUDMatch
from app.models.match import Match
from app.schemas import MatchCreateDTO, MatchUpdateDTO
from app.services.errors import BadRequestError, NotFoundError


class MatchService:
    def __init__(self, match_crud: CRUDMatch):
        self.match_crud = match_crud

    # ---------- helpers ----------

    @staticmethod
    def _validate_winner_is_participant(
        home_team_id: UUID, away_team_id: UUID, winner_team_id: UUID | None
    ) -> None:
        if winner_team_id and winner_team_id not in {home_team_id, away_team_id}:
            raise BadRequestError(
                "winner_team_id must be either home_team_id or away_team_id",
                code="WINNER_NOT_A_PARTICIPANT",
                details={"winner_team_id": str(winner_team_id)},
            )

    @staticmethod
    def _coerce_or_validate_winner(
        *,
        home_team_id: UUID,
        away_team_id: UUID,
        home_score: int | None,
        away_score: int | None,
        winner_team_id: UUID | None,
    ) -> UUID | None:
        """
        If scores are provided, infer winner.
        If winner provided, validate against scores.
        """
        if home_score is None or away_score is None:
            MatchService._validate_winner_is_participant(
                home_team_id, away_team_id, winner_team_id
            )
            return winner_team_id

        if home_score == away_score:
            raise BadRequestError(
                "home_team_score and away_team_score cannot be equal",
                code="DRAW_NOT_ALLOWED",
            )

        inferred = home_team_id if home_score > away_score else away_team_id
        if winner_team_id is None:
            return inferred

        if winner_team_id != inferred:
            raise BadRequestError(
                "winner_team_id disagrees with scores",
                code="WINNER_SCORE_MISMATCH",
                details={
                    "home_team_id": str(home_team_id),
                    "away_team_id": str(away_team_id),
                    "home_team_score": home_score,
                    "away_team_score": away_score,
                    "inferred_winner": str(inferred),
                    "winner_team_id": str(winner_team_id),
                },
            )
        return winner_team_id

    # ---------- CRUD ----------

    def get_by_id(self, db: Session, match_id: UUID) -> Match:
        db_match = self.match_crud.get(db=db, id=match_id)
        if not db_match:
            raise NotFoundError(
                "Match not found",
                code="MATCH_NOT_FOUND",
                details={"match_id": str(match_id)},
            )
        return db_match

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 0,
        season_id: UUID | None = None,
        team_id: UUID | None = None,
        winner_team_id: UUID | None = None,
        arena_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Sequence[Match]:
        return self.match_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            season_id=season_id,
            team_id=team_id,
            winner_team_id=winner_team_id,
            arena_id=arena_id,
            date_from=date_from,
            date_to=date_to,
        )

    def create(self, db: Session, match_in: MatchCreateDTO) -> Match:
        winner = self._coerce_or_validate_winner(
            home_team_id=match_in.home_team_id,
            away_team_id=match_in.away_team_id,
            home_score=match_in.home_team_score,
            away_score=match_in.away_team_score,
            winner_team_id=match_in.winner_team_id,
        )

        payload = match_in.model_copy(update={"winner_team_id": winner})
        return self.match_crud.create(db=db, obj_in=payload)

    def update(self, db: Session, match_id: UUID, match_in: MatchUpdateDTO) -> Match:
        db_match = self.get_by_id(db=db, match_id=match_id)

        data = match_in.model_dump(exclude_unset=True)
        home_team_id = data.get("home_team_id", db_match.home_team_id)
        away_team_id = data.get("away_team_id", db_match.away_team_id)
        home_score = data.get("home_team_score", db_match.home_team_score)
        away_score = data.get("away_team_score", db_match.away_team_score)
        winner_team_id = data.get("winner_team_id", db_match.winner_team_id)

        winner = self._coerce_or_validate_winner(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_score=home_score,
            away_score=away_score,
            winner_team_id=winner_team_id,
        )

        match_in = match_in.model_copy(update={"winner_team_id": winner})
        return self.match_crud.update(db=db, db_obj=db_match, obj_in=match_in)

    def delete(self, db: Session, match_id: UUID) -> Match:
        db_match = self.get_by_id(db=db, match_id=match_id)

        return self.match_crud.remove(db=db, db_obj=db_match)
