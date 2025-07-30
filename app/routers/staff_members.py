from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from uuid import UUID

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/staff-members",
    tags=["Staff Members"]
)

""" @router.post("/", response_model=schemas.StaffMember)
def create_arena(arena: schemas.ArenaCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_arena(db=db, arena=arena)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Arena with name '{arena.name}' already exists."
        ) """

@router.get("/", response_model=List[schemas.StaffMember])
def read_staff_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    staff_members = crud.get_staff_members(db, skip=skip, limit=limit)
    return staff_members

@router.get("/{staff_member_id}", response_model=schemas.StaffMember)
def read_staff_member(staff_member_id: UUID, db: Session = Depends(get_db)):
    db_staff_member = crud.get_staff_member(db, staff_member_id=staff_member_id)
    if db_staff_member is None:
        raise HTTPException(status_code=404, detail="Staff Member not found")
    return db_staff_member

""" @router.put("/{arena_id}", response_model=schemas.Arena)
def update_arena(arena_id: UUID, arena: schemas.ArenaUpdate, db: Session = Depends(get_db)):
    db_arena = crud.update_arena(db, arena_id=arena_id, arena_update=arena)
    if db_arena is None:
        raise HTTPException(status_code=404, detail="Arena not found")
    return db_arena

@router.delete("/{arena_id}", response_model=schemas.Arena)
def delete_arena(arena_id: UUID, db: Session = Depends(get_db)):
    db_arena = crud.delete_arena(db, arena_id=arena_id)
    if db_arena is None:
        raise HTTPException(status_code=404, detail="Arena not found")
    return db_arena """
