from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import season_service

router = APIRouter(prefix="/season", tags=["Season"])


@router.post("/", response_model=models.SeasonRead, status_code=status.HTTP_201_CREATED)
def create_season_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    season_in: models.SeasonCreate,
):
    return season_service.create(db=db, season_in=season_in)


@router.get("/", response_model=list[models.SeasonRead])
def read_seasons_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return season_service.get_all(db=db, skip=skip, limit=limit)


@router.get("/{season_id}", response_model=models.SeasonRead)
def read_season_endpoint(*, db: Session = Depends(deps.get_db), season_id: UUID):
    return season_service.get_by_id(db=db, season_id=season_id)


@router.patch("/{season_id}", response_model=models.SeasonRead)
def update_season_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    season_id: UUID,
    season_in: models.SeasonUpdate,
):
    return season_service.update(db=db, season_id=season_id, season_in=season_in)


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_season_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    season_id: UUID,
):
    season_service.delete(db=db, season_id=season_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
