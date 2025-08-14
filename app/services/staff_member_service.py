from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_staff_member import CRUDStaffMember


class StaffMemberService:
    def __init__(self, staff_member_crud: CRUDStaffMember):
        self.staff_member_crud = staff_member_crud

    def get_by_id(self, db: Session, staff_member_id: UUID) -> models.StaffMember:
        db_staff_member = self.staff_member_crud.get(db=db, id=staff_member_id)
        if not db_staff_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found"
            )
        return db_staff_member

    def get_all(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[models.StaffMember]:
        return self.staff_member_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(
        self, db: Session, staff_member_in: models.StaffMemberCreate
    ) -> models.StaffMember:
        return self.staff_member_crud.create(db=db, obj_in=staff_member_in)

    def update(
        self,
        db: Session,
        staff_member_id: UUID,
        staff_member_in: models.StaffMemberUpdate,
    ) -> models.StaffMember:
        db_staff_member = self.get_by_id(db=db, staff_member_id=staff_member_id)
        return self.staff_member_crud.update(
            db=db, db_obj=db_staff_member, obj_in=staff_member_in
        )

    def delete(self, db: Session, staff_member_id: UUID) -> models.StaffMember:
        db_staff_member = self.get_by_id(db=db, staff_member_id=staff_member_id)
        return self.staff_member_crud.remove(db=db, db_obj=db_staff_member)


staff_member_service = StaffMemberService(crud.staff_member)
