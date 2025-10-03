from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.team import TeamType
from app.schemas import TeamCreateDTO, TeamReadDTO, TeamUpdateDTO
from app.services.team_service import TeamService

router = APIRouter(
    prefix="/team",
    tags=["Team"],
)


@router.post("/", response_model=TeamReadDTO, status_code=status.HTTP_201_CREATED)
def create_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_in: TeamCreateDTO,
    service: TeamService = Depends(deps.get_team_service),
):
    return service.create(db=db, team_in=team_in)


@router.get("/", response_model=list[TeamReadDTO])
def get_teams_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    team_type: TeamType | None = None,
    country_code: str | None = None,
    home_arena_id: UUID | None = None,
    search: str | None = None,
    service: TeamService = Depends(deps.get_team_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        team_type=team_type,
        country_code=country_code,
        home_arena_id=home_arena_id,
        search=search,
    )


@router.get("/{team_id}", response_model=TeamReadDTO)
def get_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_id: UUID,
    service: TeamService = Depends(deps.get_team_service),
):
    return service.get_by_id(db=db, team_id=team_id)


@router.patch("/{team_id}", response_model=TeamReadDTO)
def update_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_id: UUID,
    team_in: TeamUpdateDTO,
    service: TeamService = Depends(deps.get_team_service),
):
    return service.update(db=db, team_id=team_id, team_in=team_in)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    team_id: UUID,
    service: TeamService = Depends(deps.get_team_service),
):
    service.delete(db=db, team_id=team_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
