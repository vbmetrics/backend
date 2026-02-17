from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.user import UserRole
from app.schemas import (
    PlayerTeamHistoryCreateDTO,
    PlayerTeamHistoryReadDTO,
    PlayerTeamHistoryUpdateDTO,
)
from app.services.player_team_history_service import PlayerTeamHistoryService

router = APIRouter(
    prefix="/player-team-history",
    tags=["Player-Team History"],
)


@router.post(
    "/",
    response_model=PlayerTeamHistoryReadDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def create_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    history_in: PlayerTeamHistoryCreateDTO,
    service: PlayerTeamHistoryService = Depends(deps.get_player_team_history_service),
):
    return service.create(db=db, history_in=history_in)


@router.get(
    "/",
    response_model=list[PlayerTeamHistoryReadDTO],
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_player_team_histories_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    player_id: UUID | None = None,
    team_id: UUID | None = None,
    season_id: list[UUID] | None = Query(default=None),
    active_on: date | None = None,
    service: PlayerTeamHistoryService = Depends(deps.get_player_team_history_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        player_id=player_id,
        team_id=team_id,
        season_id=season_id,
        active_on=active_on,
    )


@router.get(
    "/{pth_id}",
    response_model=PlayerTeamHistoryReadDTO,
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    pth_id: UUID,
    service: PlayerTeamHistoryService = Depends(deps.get_player_team_history_service),
):
    return service.get_by_id(db=db, pth_id=pth_id)


@router.patch(
    "/{pth_id}",
    response_model=PlayerTeamHistoryReadDTO,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def update_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    pth_id: UUID,
    history_in: PlayerTeamHistoryUpdateDTO,
    service: PlayerTeamHistoryService = Depends(deps.get_player_team_history_service),
):
    return service.update(db=db, pth_id=pth_id, history_in=history_in)


@router.delete(
    "/{pth_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def delete_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    pth_id: UUID,
    service: PlayerTeamHistoryService = Depends(deps.get_player_team_history_service),
):
    service.delete(db=db, pth_id=pth_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
