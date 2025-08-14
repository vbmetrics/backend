from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import staff_member_service

router = APIRouter(
    prefix="/staff-member",
    tags=["Staff Member"],
)


@router.post(
    "/", response_model=models.StaffMemberRead, status_code=status.HTTP_201_CREATED
)
def create_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_in: models.StaffMemberCreate,
):
    return staff_member_service.create(db=db, staff_member_in=staff_member_in)


@router.get("/", response_model=list[models.StaffMemberRead])
def read_staff_members_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return staff_member_service.get_all(db=db, skip=skip, limit=limit)


@router.get("/{staff_member_id}", response_model=models.StaffMemberRead)
def read_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_id: UUID,
):
    return staff_member_service.get_by_id(db=db, staff_member_id=staff_member_id)


@router.patch("/{staff_member_id}", response_model=models.StaffMemberRead)
def update_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_id: UUID,
    staff_member_in: models.StaffMemberUpdate,
):
    return staff_member_service.update(
        db=db, staff_member_id=staff_member_id, staff_member_in=staff_member_in
    )


@router.delete("/{staff_member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_member_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    staff_member_id: UUID,
):
    staff_member_service.delete(db=db, staff_member_id=staff_member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
