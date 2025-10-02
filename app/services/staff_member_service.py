from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_staff_member import CRUDStaffMember
from app.models.staff_member import StaffMember, StaffRoleType
from app.schemas import StaffMemberCreateDTO, StaffMemberUpdateDTO
from app.services.errors import BadRequestError, NotFoundError


class StaffMemberService:
    def __init__(self, staff_member_crud: CRUDStaffMember):
        self.staff_crud = staff_member_crud

    def get_by_id(self, db: Session, staff_id: UUID) -> StaffMember:
        db_staff = self.staff_crud.get(db=db, id=staff_id)
        if not db_staff:
            raise NotFoundError(
                "Staff member not found",
                code="STAFF_NOT_FOUND",
                details={"staff_id": str(staff_id)},
            )
        return db_staff

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        nationality_code: str | None = None,
        role_type: StaffRoleType | None = None,
        search: str | None = None,
    ) -> Sequence[StaffMember]:
        return self.staff_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            nationality_code=nationality_code,
            role_type=role_type,
            search=search,
        )

    def create(self, db: Session, staff_in: StaffMemberCreateDTO) -> StaffMember:
        if len(staff_in.nationality_code) != 2:
            raise BadRequestError(
                "nationality_code must be 2 letters", code="INVALID_COUNTRY_CODE"
            )
        return self.staff_crud.create(db=db, obj_in=staff_in)

    def update(
        self, db: Session, staff_id: UUID, staff_in: StaffMemberUpdateDTO
    ) -> StaffMember:
        obj = self.get_by_id(db=db, staff_id=staff_id)
        return self.staff_crud.update(db=db, db_obj=obj, obj_in=staff_in)

    def delete(self, db: Session, staff_id: UUID) -> StaffMember:
        obj = self.get_by_id(db=db, staff_id=staff_id)
        return self.staff_crud.remove(db=db, db_obj=obj)
