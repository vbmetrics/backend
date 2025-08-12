from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import StaffMember, StaffMemberCreate, StaffMemberUpdate


class CRUDStaffMember(CRUDBase[StaffMember, StaffMemberCreate, StaffMemberUpdate]):
    def get(self, db: Session, id: UUID) -> StaffMember | None:
        """
        Overwrites get method to add eager loading for 'nationality' relationship.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.nationality))  # type: ignore[arg-type]
        )
        return db.exec(statement).first()


staff_member = CRUDStaffMember(StaffMember)
