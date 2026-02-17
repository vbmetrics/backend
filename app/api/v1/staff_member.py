from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.user import UserRole  # <--- NOWY IMPORT
from app.schemas import StaffMemberCreateDTO, StaffMemberReadDTO, StaffMemberUpdateDTO
from app.services.staff_member_service import StaffMemberService

router = APIRouter(
    prefix="/staff-member",
    tags=["Staff Member"],
)


@router.post(
    "/",
    response_model=StaffMemberReadDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def create_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_in: StaffMemberCreateDTO,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.create(db=db, staff_member_in=staff_member_in)


@router.get(
    "/",
    response_model=list[StaffMemberReadDTO],
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_staff_members_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    nationality_code: str | None = None,
    search: str | None = None,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        nationality_code=nationality_code,
        search=search,
    )


@router.get(
    "/{staff_member_id}",
    response_model=StaffMemberReadDTO,
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_id: UUID,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.get_by_id(db=db, staff_member_id=staff_member_id)


@router.patch(
    "/{staff_member_id}",
    response_model=StaffMemberReadDTO,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def update_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_id: UUID,
    staff_member_in: StaffMemberUpdateDTO,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.update(
        db=db, staff_member_id=staff_member_id, staff_member_in=staff_member_in
    )


@router.delete(
    "/{staff_member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def delete_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_id: UUID,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    service.delete(db=db, staff_member_id=staff_member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
