from collections.abc import Sequence
from datetime import date
from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.player_team_history import PlayerTeamHistory
from app.schemas import (
    PlayerTeamHistoryCreateDTO,
    PlayerTeamHistoryUpdateDTO,
)


class CRUDPlayerTeamHistory(
    CRUDBase[PlayerTeamHistory, PlayerTeamHistoryCreateDTO, PlayerTeamHistoryUpdateDTO]
):
    def get(self, db: Session, id: UUID) -> PlayerTeamHistory | None:
        """
        Overwrites get method to add eager loading
        for 'player', 'team' and 'season' relationship.
        """
        statement = select(self.model).where(self.model.id == id)
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
        active_on: date | None = None,
    ) -> Sequence[PlayerTeamHistory]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model)

        # Cast columns to Any for mypy (optional columns in typing)
        player_col: Any = self.model.player_id
        team_col: Any = self.model.team_id
        season_col: Any = self.model.season_id
        start_col: Any = self.model.start_date
        end_col: Any = self.model.end_date

        if player_id:
            statement = statement.where(player_col == player_id)
        if team_id:
            statement = statement.where(team_col == team_id)
        if season_id:
            statement = statement.where(season_col == season_id)
        if active_on:
            statement = statement.where(start_col <= active_on).where(
                (end_col.is_(None)) | (end_col >= active_on)
            )  # type: ignore[attr-defined]

        statement = (
            statement.order_by(start_col.desc(), end_col.desc())
            .offset(skip)
            .limit(limit)
        )
        return cast(Sequence[PlayerTeamHistory], db.exec(statement).all())

    def any_overlapping(
        self,
        db: Session,
        *,
        player_id: UUID,
        season_id: UUID,
        start_date: date,
        end_date: date | None,
        exclude_id: UUID | None = None,
    ) -> bool:
        m = self.model
        start_col: Any = m.start_date
        end_col: Any = m.end_date
        player_col: Any = m.player_id
        season_col: Any = m.season_id

        statement = (
            select(m).where(player_col == player_id).where(season_col == season_id)
        )

        # Overlap condition:
        # (existing.start <= new_end OR new_end IS NULL)
        # AND
        # (existing.end IS NULL OR existing.end >= new_start)
        if end_date is not None:
            statement = statement.where(start_col <= end_date)
        # existing.end IS NULL OR existing.end >= new_start
        statement = statement.where((end_col.is_(None)) | (end_col >= start_date))  # type: ignore[attr-defined]

        if exclude_id:
            statement = statement.where(m.id != exclude_id)

        return db.exec(statement).first() is not None


player_team_history = CRUDPlayerTeamHistory(PlayerTeamHistory)
