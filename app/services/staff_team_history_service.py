from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_staff_team_history import CRUDStaffTeamHistory
from app.models.staff_team_history import StaffTeamHistory
from app.schemas import (
    StaffTeamHistoryCreateDTO,
    StaffTeamHistoryUpdateDTO,
)
from app.services.errors import ConflictError, NotFoundError


class StaffTeamHistoryService:
    def __init__(self, staff_team_history_crud: CRUDStaffTeamHistory):
        self.sth_crud = staff_team_history_crud

    def get_by_id(self, db: Session, sth_id: UUID) -> StaffTeamHistory:
        db_history = self.sth_crud.get(db=db, id=sth_id)
        if not db_history:
            raise NotFoundError(
                "Staff team history not found",
                code="STH_NOT_FOUND",
                details={"id": str(sth_id)},
            )
        return db_history

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        staff_member_id: UUID | None = None,
        team_id: UUID | None = None,
        season_id: UUID | None = None,
    ) -> Sequence[StaffTeamHistory]:
        return self.sth_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            staff_member_id=staff_member_id,
            team_id=team_id,
            season_id=season_id,
        )

    def create(
        self, db: Session, sth_in: StaffTeamHistoryCreateDTO
    ) -> StaffTeamHistory:
        if self.sth_crud.exists_for_season(
            db, staff_member_id=sth_in.staff_member_id, season_id=sth_in.season_id
        ):
            raise ConflictError(
                "Staff member already assigned in this season",
                code="STH_SEASON_CONFLICT",
                details={
                    "staff_member_id": str(sth_in.staff_member_id),
                    "season_id": str(sth_in.season_id),
                },
            )
        return self.sth_crud.create(db=db, obj_in=sth_in)

    def update(
        self, db: Session, sth_id: UUID, sth_in: StaffTeamHistoryUpdateDTO
    ) -> StaffTeamHistory:
        obj = self.get_by_id(db=db, sth_id=sth_id)
        return self.sth_crud.update(db=db, db_obj=obj, obj_in=sth_in)

    def delete(self, db: Session, sth_id: UUID) -> StaffTeamHistory:
        obj = self.get_by_id(db=db, sth_id=sth_id)
        return self.sth_crud.remove(db=db, db_obj=obj)
