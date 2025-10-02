from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.staff_team_history import StaffTeamHistory
from app.schemas import (
    StaffTeamHistoryCreateDTO,
    StaffTeamHistoryUpdateDTO,
)


class CRUDStaffTeamHistory(
    CRUDBase[StaffTeamHistory, StaffTeamHistoryCreateDTO, StaffTeamHistoryUpdateDTO]
):
    def get(self, db: Session, id: UUID) -> StaffTeamHistory | None:
        """
        Overwrites get method to add eager loading
        for 'staff_member', 'team' and 'season' relationship.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        staff_member_id: UUID | None = None,
        team_id: UUID | None = None,
        season_id: UUID | None = None,
    ) -> Sequence[StaffTeamHistory]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model)

        staff_col: Any = self.model.staff_member_id
        team_col: Any = self.model.team_id
        season_col: Any = self.model.season_id
        created_col: Any = self.model.created_at

        if staff_member_id:
            statement = statement.where(staff_col == staff_member_id)
        if team_id:
            statement = statement.where(team_col == team_id)
        if season_id:
            statement = statement.where(season_col == season_id)

        statement = (
            statement.order_by(season_col, created_col).offset(skip).limit(limit)
        )
        return cast(Sequence[StaffTeamHistory], db.exec(statement).all())

    def exists_for_season(
        self, db: Session, *, staff_member_id: UUID, season_id: UUID
    ) -> bool:
        m = self.model
        statement = select(m).where(
            m.staff_member_id == staff_member_id, m.season_id == season_id
        )
        return db.exec(statement).first() is not None


staff_team_history = CRUDStaffTeamHistory(StaffTeamHistory)
