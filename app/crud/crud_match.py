from collections.abc import Sequence
from datetime import date
from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.match import Match
from app.schemas import MatchCreateDTO, MatchUpdateDTO


class CRUDMatch(CRUDBase[Match, MatchCreateDTO, MatchUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Match | None:
        """
        Overwrites get method to add eager loading for relationships.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        season_id: UUID | None = None,
        team_id: UUID | None = None,
        winner_team_id: UUID | None = None,
        arena_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Sequence[Match]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model)

        # Cast columns to Any so mypy doesn't treat them as Optional[...] here
        home_team_col: Any = self.model.home_team_id
        away_team_col: Any = self.model.away_team_id
        season_col: Any = self.model.season_id
        winner_col: Any = self.model.winner_team_id
        arena_col: Any = self.model.arena_id
        match_date_col: Any = self.model.match_date
        created_at_col: Any = self.model.created_at

        if season_id:
            statement = statement.where(season_col == season_id)
        if team_id:
            statement = statement.where(
                (home_team_col == team_id) | (away_team_col == team_id)
            )
        if winner_team_id:
            statement = statement.where(winner_col == winner_team_id)
        if arena_id:
            statement = statement.where(arena_col == arena_id)
        if date_from:
            statement = statement.where(match_date_col >= date_from)
        if date_to:
            statement = statement.where(match_date_col <= date_to)

        statement = (
            statement.order_by(match_date_col, created_at_col).offset(skip).limit(limit)
        )
        return cast(Sequence[Match], db.exec(statement).all())


match = CRUDMatch(Match)
