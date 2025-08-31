from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Match, MatchCreate, MatchUpdate


class CRUDMatch(CRUDBase[Match, MatchCreate, MatchUpdate]):
    def get(self, db: Session, id: UUID) -> Match | None:
        """
        Overwrites get method to add eager loading for relationships.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.season),  # type: ignore[arg-type]
                selectinload(self.model.arena),  # type: ignore[arg-type]
                selectinload(self.model.home_team),  # type: ignore[arg-type]
                selectinload(self.model.away_team),  # type: ignore[arg-type]
                selectinload(self.model.winner_team),  # type: ignore[arg-type]
            )
        )
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
    ) -> Sequence[Match]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model).order_by(
            self.model.match_date.desc().nulls_last()  # type: ignore
        )

        if season_id:
            statement = statement.where(self.model.season_id == season_id)

        if winner_team_id:
            statement = statement.where(self.model.winner_team_id == winner_team_id)

        if team_id:
            statement = statement.where(
                or_(
                    self.model.home_team_id == team_id,  # type: ignore
                    self.model.away_team_id == team_id,  # type: ignore
                )
            )

        statement = (
            statement.offset(skip)
            .limit(limit)
            .options(
                selectinload(self.model.season),  # type: ignore[arg-type]
                selectinload(self.model.home_team),  # type: ignore[arg-type]
                selectinload(self.model.away_team),  # type: ignore[arg-type]
            )
        )
        return db.exec(statement).all()


match = CRUDMatch(Match)
