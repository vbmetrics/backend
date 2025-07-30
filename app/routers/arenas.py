from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from uuid import UUID

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/arenas",
    tags=["Arenas"]
)

@router.post("/", response_model=schemas.Arena)
def create_arena(arena: schemas.ArenaCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_arena(db=db, arena=arena)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Arena with name '{arena.name}' already exists."
        )

@router.get("/", response_model=List[schemas.Arena])
def read_arenas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    arenas = crud.get_arenas(db, skip=skip, limit=limit)
    return arenas

@router.get("/{arena_id}", response_model=schemas.Arena)
def read_arena(arena_id: UUID, db: Session = Depends(get_db)):
    db_arena = crud.get_arena(db, arena_id=arena_id)
    if db_arena is None:
        raise HTTPException(status_code=404, detail="Arena not found")
    return db_arena
