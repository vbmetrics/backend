# app/routers/seasons.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/seasons",
    tags=["Seasons"]
)

@router.post("/", response_model=schemas.Season)
def create_season(season: schemas.SeasonCreate, db: Session = Depends(get_db)):
    return crud.create_season(db=db, season=season)

@router.get("/", response_model=List[schemas.Season])
def read_seasons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    seasons = crud.get_seasons(db, skip=skip, limit=limit)
    return seasons

@router.get("/{season_id}", response_model=schemas.Season)
def read_season(season_id: UUID, db: Session = Depends(get_db)):
    db_season = crud.get_season(db, season_id=season_id)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return db_season
