from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from typing import List, Optional

from .. import crud, models
from ..database import get_session


router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)

class TeamReadWithDetails(models.TeamRead):
    country: Optional[models.CountryRead] = None
    home_arena: Optional[models.ArenaRead] = None

@router.post("/", response_model=models.TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(team: models.TeamCreate, session: Session = Depends(get_session)):
    return crud.create_team(session=session, team=team)

@router.get("/", response_model=List[models.TeamRead])
def read_teams(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return crud.get_teams(session=session, skip=skip, limit=limit)

@router.get("/{team_id}", response_model=TeamReadWithDetails)
def read_team(team_id: UUID, session: Session = Depends(get_session)):
    db_team = crud.get_team(session=session, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.patch("/{team_id}", response_model=models.TeamRead)
def update_team(team_id: UUID, team_update: models.TeamUpdate, session: Session = Depends(get_session)):
    db_team = session.get(models.Team, team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return crud.update_team(session=session, db_team=db_team, team_update=team_update)

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: UUID, session: Session = Depends(get_session)):
    db_team = session.get(models.Team, team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    
    crud.delete_team(session=session, db_team=db_team)
    return
