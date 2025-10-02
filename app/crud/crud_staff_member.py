from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import or_
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.staff_member import StaffMember, StaffRoleType
from app.schemas import StaffMemberCreateDTO, StaffMemberUpdateDTO


class CRUDStaffMember(
    CRUDBase[StaffMember, StaffMemberCreateDTO, StaffMemberUpdateDTO]
):
    def get(self, db: Session, id: UUID) -> StaffMember | None:
        """
        Overwrites get method to add eager loading for 'nationality' relationship.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        nationality_code: str | None = None,
        role_type: StaffRoleType | None = None,
        search: str | None = None,  # first/last name
    ) -> Sequence[StaffMember]:
        statement = select(self.model)

        nat_col: Any = self.model.nationality_code
        role_col: Any = self.model.role_type
        first_col: Any = self.model.first_name
        last_col: Any = self.model.last_name

        if nationality_code:
            statement = statement.where(nat_col == nationality_code)
        if role_type:
            statement = statement.where(role_col == role_type)
        if search:
            ilike = f"%{search}%"
            statement = statement.where(
                or_(first_col.ilike(ilike), last_col.ilike(ilike))
            )  # type: ignore[attr-defined]

        statement = statement.order_by(last_col, first_col).offset(skip).limit(limit)
        return cast(Sequence[StaffMember], db.exec(statement).all())


staff_member = CRUDStaffMember(StaffMember)
