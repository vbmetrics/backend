from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.staff_member import StaffRoleType
from app.schemas import StaffMemberCreateDTO, StaffMemberReadDTO, StaffMemberUpdateDTO
from app.services.staff_member_service import StaffMemberService

router = APIRouter(
    prefix="/staff-member",
    tags=["Staff Member"],
)


@router.post(
    "/", response_model=StaffMemberReadDTO, status_code=status.HTTP_201_CREATED
)
def create_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_in: StaffMemberCreateDTO,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.create(db=db, staff_in=staff_in)


@router.get("/", response_model=list[StaffMemberReadDTO])
def read_staff_members_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    nationality_code: str | None = None,
    role_type: StaffRoleType | None = None,
    search: str | None = None,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        nationality_code=nationality_code,
        role_type=role_type,
        search=search,
    )


@router.get("/{staff_id}", response_model=StaffMemberReadDTO)
def read_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_id: UUID,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.get_by_id(db=db, staff_id=staff_id)


@router.patch("/{staff_id}", response_model=StaffMemberReadDTO)
def update_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_id: UUID,
    staff_in: StaffMemberUpdateDTO,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    return service.update(db=db, staff_id=staff_id, staff_in=staff_in)


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_id: UUID,
    service: StaffMemberService = Depends(deps.get_staff_member_service),
):
    service.delete(db=db, staff_id=staff_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
