from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_staff_team_history import CRUDStaffTeamHistory


class StaffTeamHistoryService:
    def __init__(self, staff_team_history_crud: CRUDStaffTeamHistory):
        self.staff_team_history_crud = staff_team_history_crud

    def get_by_id(self, db: Session, history_id: UUID) -> models.StaffTeamHistory:
        db_history = self.staff_team_history_crud.get(db=db, id=history_id)
        if not db_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff-Team History record not found",
            )
        return db_history

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[models.StaffTeamHistory]:
        return self.staff_team_history_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(
        self, db: Session, history_in: models.StaffTeamHistoryCreate
    ) -> models.StaffTeamHistory:
        return self.staff_team_history_crud.create(db=db, obj_in=history_in)

    def update(
        self,
        db: Session,
        history_id: UUID,
        history_in: models.StaffTeamHistoryUpdate,
    ) -> models.StaffTeamHistory:
        db_history = self.get_by_id(db=db, history_id=history_id)
        return self.staff_team_history_crud.update(
            db=db, db_obj=db_history, obj_in=history_in
        )

    def delete(self, db: Session, history_id: UUID) -> models.StaffTeamHistory:
        db_history = self.get_by_id(db=db, history_id=history_id)
        return self.staff_team_history_crud.remove(db=db, db_obj=db_history)


staff_team_history_service = StaffTeamHistoryService(crud.staff_team_history)
