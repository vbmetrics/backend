from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import team_service

router = APIRouter(
    prefix="/team",
    tags=["Team"],
)


@router.post("/", response_model=models.TeamRead, status_code=status.HTTP_201_CREATED)
def create_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_in: models.TeamCreate,
):
    return team_service.create(db=db, team_in=team_in)


@router.get("/", response_model=list[models.TeamRead])
def get_teams_endpoint(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return team_service.get_all(db=db, skip=skip, limit=limit)


@router.get("/{team_id}", response_model=models.TeamRead)
def get_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_id: UUID,
):
    return team_service.get_by_id(db=db, team_id=team_id)


@router.patch("/{team_id}", response_model=models.TeamRead)
def update_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_id: UUID,
    team_in: models.TeamUpdate,
):
    return team_service.update(db=db, team_id=team_id, team_in=team_in)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_id: UUID,
):
    team_service.delete(db=db, team_id=team_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
