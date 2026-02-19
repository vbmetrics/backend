from collections.abc import Sequence
from datetime import date
from typing import Any
from uuid import UUID

# NOWY IMPORT
from sqlalchemy.orm import joinedload
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
        # DODANO OPTIONS JOINEDLOAD
        statement = (
            select(self.model)
            .options(joinedload(self.model.player))
            .where(self.model.id == id)
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
        season_id: list[UUID] | None = None,
        active_on: date | None = None,
    ) -> Sequence[PlayerTeamHistory]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        # DODANO OPTIONS JOINEDLOAD
        query = select(PlayerTeamHistory).options(joinedload(PlayerTeamHistory.player))

        if player_id:
            query = query.where(PlayerTeamHistory.player_id == player_id)

        if team_id:
            query = query.where(PlayerTeamHistory.team_id == team_id)

        # KLUCZOWA ZMIANA: Obsługa listy sezonów w bazie danych
        if season_id:
            query = query.where(PlayerTeamHistory.season_id.in_(season_id))

        if active_on:
            query = query.where(
                (PlayerTeamHistory.start_date <= active_on)
                & (
                    (PlayerTeamHistory.end_date >= active_on)
                    | (PlayerTeamHistory.end_date is None)
                )
            )

        query = query.offset(skip).limit(limit)
        return db.exec(query).all()

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
        # ... (ta metoda zostaje bez zmian) ...
        m = self.model
        start_col: Any = m.start_date
        end_col: Any = m.end_date
        player_col: Any = m.player_id
        season_col: Any = m.season_id

        statement = (
            select(m).where(player_col == player_id).where(season_col == season_id)
        )

        if end_date is not None:
            statement = statement.where(start_col <= end_date)
        statement = statement.where((end_col.is_(None)) | (end_col >= start_date))  # type: ignore[attr-defined]

        if exclude_id:
            statement = statement.where(m.id != exclude_id)

        return db.exec(statement).first() is not None


player_team_history = CRUDPlayerTeamHistory(PlayerTeamHistory)
