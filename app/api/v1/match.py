from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import match_service

router = APIRouter(prefix="/match", tags=["Match"])


@router.post("/", response_model=models.MatchRead, status_code=status.HTTP_201_CREATED)
def create_match_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_in: models.MatchCreate,
):
    return match_service.create(db=db, match_in=match_in)


@router.get("/", response_model=list[models.MatchRead])
def read_matches_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    season_id: UUID | None = None,
    team_id: UUID | None = None,
    winner_team_id: UUID | None = None,
):
    return match_service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        season_id=season_id,
        team_id=team_id,
        winner_team_id=winner_team_id,
    )


@router.get("/{match_id}", response_model=models.MatchRead)
def read_match_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
):
    return match_service.get_by_id(db=db, match_id=match_id)


@router.patch("/{match_id}", response_model=models.MatchRead)
def update_match_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    match_in: models.MatchUpdate,
):
    return match_service.update(db=db, match_id=match_id, match_in=match_in)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
):
    match_service.delete(db=db, match_id=match_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
