from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from uuid import UUID

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/staff-team-history",
    tags=["Staff-Team History"]
)

@router.post("/", response_model=schemas.StaffTeamHistory)
def create_staff_team_history(staff_team_history: schemas.StaffTeamHistoryCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_staff_team_history(db=db, staff_team_history=staff_team_history)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Staff-Team History already exists."
        )

@router.get("/", response_model=List[schemas.StaffTeamHistory])
def read_staff_team_histories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    staff_team_histories = crud.get_staff_team_histories(db, skip=skip, limit=limit)
    return staff_team_histories

@router.get("/{staff_team_history_id}", response_model=schemas.StaffTeamHistory)
def read_staff_team_history(staff_team_history_id: UUID, db: Session = Depends(get_db)):
    db_staff_team_history = crud.get_staff_team_history(db, staff_team_history_id=staff_team_history_id)
    if db_staff_team_history is None:
        raise HTTPException(status_code=404, detail="Staff-Team History not found")
    return db_staff_team_history

@router.put("/{staff_team_history_id}", response_model=schemas.StaffTeamHistory)
def update_staff_team_history(staff_team_history_id: UUID, staff_team_history: schemas.StaffTeamHistoryUpdate, db: Session = Depends(get_db)):
    db_staff_team_history = crud.update_staff_team_history(db, staff_team_history_id=staff_team_history_id, staff_team_history_update=staff_team_history)
    if db_staff_team_history is None:
        raise HTTPException(status_code=404, detail="Staff-Team History not found")
    return db_staff_team_history

@router.delete("/{staff_team_history_id}", response_model=schemas.StaffTeamHistory)
def delete_staff_team_history(staff_team_history_id: UUID, db: Session = Depends(get_db)):
    db_staff_team_history = crud.delete_staff_team_history(db, staff_team_history_id=staff_team_history_id)
    if db_staff_team_history is None:
        raise HTTPException(status_code=404, detail="Staff-Team History not found")
    return db_staff_team_history
