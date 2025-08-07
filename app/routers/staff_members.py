# NOWY PLIK: routers/staff_members.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from typing import List, Optional

from .. import crud, models
from ..database import get_session


router = APIRouter(
    prefix="/staff-members",
    tags=["Staff Members"],
)

class StaffMemberReadWithNationality(models.StaffMemberRead):
    nationality: Optional[models.CountryRead] = None


@router.post("/", response_model=models.StaffMemberRead, status_code=status.HTTP_201_CREATED)
def create_staff_member(staff_member: models.StaffMemberCreate, session: Session = Depends(get_session)):
    return crud.create_staff_member(session=session, staff_member=staff_member)


@router.get("/", response_model=List[models.StaffMemberRead])
def read_staff_members(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return crud.get_staff_members(session=session, skip=skip, limit=limit)


@router.get("/{staff_member_id}", response_model=StaffMemberReadWithNationality)
def read_staff_member(staff_member_id: UUID, session: Session = Depends(get_session)):
    db_staff_member = crud.get_staff_member(session=session, staff_member_id=staff_member_id)
    if db_staff_member is None:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return db_staff_member


@router.patch("/{staff_member_id}", response_model=models.StaffMemberRead)
def update_staff_member(staff_member_id: UUID, staff_member_update: models.StaffMemberUpdate, session: Session = Depends(get_session)):
    db_staff_member = session.get(models.StaffMember, staff_member_id)
    if db_staff_member is None:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return crud.update_staff_member(session=session, db_staff_member=db_staff_member, staff_member_update=staff_member_update)


@router.delete("/{staff_member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_member(staff_member_id: UUID, session: Session = Depends(get_session)):
    db_staff_member = session.get(models.StaffMember, staff_member_id)
    if db_staff_member is None:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    crud.delete_staff_member(session=session, db_staff_member=db_staff_member)
    return
