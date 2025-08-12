from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import (
    PlayerTeamHistory,
    PlayerTeamHistoryCreate,
    PlayerTeamHistoryUpdate,
)


class CRUDPlayerTeamHistory(
    CRUDBase[PlayerTeamHistory, PlayerTeamHistoryCreate, PlayerTeamHistoryUpdate]
):
    def get(self, db: Session, id: UUID) -> PlayerTeamHistory | None:
        """
        Overwrites get method to add eager loading
        for 'player', 'team' and 'season' relationship.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.player),  # type: ignore[arg-type]
                selectinload(self.model.team),  # type: ignore[arg-type]
                selectinload(self.model.season),  # type: ignore[arg-type]
            )
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        player_id: UUID | None = None,
        team_id: UUID | None = None,
        season_id: UUID | None = None,
    ) -> Sequence[PlayerTeamHistory]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model)

        if player_id:
            statement = statement.where(self.model.player_id == player_id)
        if team_id:
            statement = statement.where(self.model.team_id == team_id)
        if season_id:
            statement = statement.where(self.model.season_id == season_id)

        statement = statement.offset(skip).limit(limit)
        return db.exec(statement).all()


player_team_history = CRUDPlayerTeamHistory(PlayerTeamHistory)
