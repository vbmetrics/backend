from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import (
    StaffTeamHistory,
    StaffTeamHistoryCreate,
    StaffTeamHistoryUpdate,
)


class CRUDStaffTeamHistory(
    CRUDBase[StaffTeamHistory, StaffTeamHistoryCreate, StaffTeamHistoryUpdate]
):
    def get(self, db: Session, id: UUID) -> StaffTeamHistory | None:
        """
        Overwrites get method to add eager loading
        for 'staff_member', 'team' and 'season' relationship.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.staff_member),  # type: ignore[arg-type]
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
        staff_member_id: UUID | None = None,
        team_id: UUID | None = None,
        season_id: UUID | None = None,
    ) -> Sequence[StaffTeamHistory]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model)

        if staff_member_id:
            statement = statement.where(self.model.staff_member_id == staff_member_id)
        if team_id:
            statement = statement.where(self.model.team_id == team_id)
        if season_id:
            statement = statement.where(self.model.season_id == season_id)

        statement = statement.offset(skip).limit(limit)
        return db.exec(statement).all()

    def get_by_foreign_keys(
        self, db: Session, *, staff_member_id: UUID, team_id: UUID, season_id: UUID
    ) -> StaffTeamHistory | None:
        statement = select(self.model).where(
            self.model.staff_member_id == staff_member_id,
            self.model.team_id == team_id,
            self.model.season_id == season_id,
        )
        return db.exec(statement).first()


staff_team_history = CRUDStaffTeamHistory(StaffTeamHistory)
