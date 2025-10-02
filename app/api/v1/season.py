from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.season import SeasonType
from app.schemas import SeasonCreateDTO, SeasonReadDTO, SeasonUpdateDTO
from app.services.season_service import SeasonService

router = APIRouter(prefix="/season", tags=["Season"])


@router.post("/", response_model=SeasonReadDTO, status_code=status.HTTP_201_CREATED)
def create_season_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    season_in: SeasonCreateDTO,
    service: SeasonService = Depends(deps.get_season_service),
):
    return service.create(db=db, season_in=season_in)


@router.get("/", response_model=list[SeasonReadDTO])
def read_seasons_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    season_type: SeasonType | None = None,
    active_on: date | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    service: SeasonService = Depends(deps.get_season_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        season_type=season_type,
        active_on=active_on,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )


@router.get("/{season_id}", response_model=SeasonReadDTO)
def read_season_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    season_id: UUID,
    service: SeasonService = Depends(deps.get_season_service),
):
    return service.get_by_id(db=db, season_id=season_id)


@router.patch("/{season_id}", response_model=SeasonReadDTO)
def update_season_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    season_id: UUID,
    season_in: SeasonUpdateDTO,
    service: SeasonService = Depends(deps.get_season_service),
):
    return service.update(db=db, season_id=season_id, season_in=season_in)


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_season_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    season_id: UUID,
    service: SeasonService = Depends(deps.get_season_service),
):
    service.delete(db=db, season_id=season_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
