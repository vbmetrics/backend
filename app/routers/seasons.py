from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from typing import List

from .. import crud, models
from ..database import get_session


router = APIRouter(
    prefix="/seasons",
    tags=["Seasons"]
)

@router.post("/", response_model=models.SeasonRead, status_code=status.HTTP_201_CREATED)
def create_season(season: models.SeasonCreate, session: Session = Depends(get_session)):
    return crud.create_season(session=session, season=season)

@router.get("/", response_model=List[models.SeasonRead])
def read_seasons(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    seasons = crud.get_seasons(session=session, skip=skip, limit=limit)
    return seasons

@router.get("/{season_id}", response_model=models.SeasonRead)
def read_season(season_id: UUID, session: Session = Depends(get_session)):
    db_season = crud.get_season(session=session, season_id=season_id)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return db_season

@router.patch("/{season_id}", response_model=models.SeasonRead)
def update_season(season_id: UUID, season_update: models.SeasonUpdate, session: Session = Depends(get_session)):
    db_season = crud.get_season(session=session, season_id=season_id)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    
    return crud.update_season(session=session, db_season=db_season, season_update=season_update)

@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_season(season_id: UUID, session: Session = Depends(get_session)):
    db_season = crud.get_season(session=session, season_id=season_id)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    
    crud.delete_season(session=session, db_season=db_season)
    return

