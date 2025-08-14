from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import player_team_history_service

router = APIRouter(
    prefix="/player-team-history",
    tags=["Player-Team History"],
)


@router.post(
    "/",
    response_model=models.PlayerTeamHistoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    history_in: models.PlayerTeamHistoryCreate,
):
    return player_team_history_service.create(db=db, history_in=history_in)


@router.get("/", response_model=list[models.PlayerTeamHistoryRead])
def read_player_team_histories_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return player_team_history_service.get_all(db=db, skip=skip, limit=limit)


@router.get("/{history_id}", response_model=models.PlayerTeamHistoryRead)
def read_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    history_id: UUID,
):
    return player_team_history_service.get_by_id(db=db, history_id=history_id)


@router.patch("/{history_id}", response_model=models.PlayerTeamHistoryRead)
def update_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    history_id: UUID,
    history_in: models.PlayerTeamHistoryUpdate,
):
    return player_team_history_service.update(
        db=db, history_id=history_id, history_in=history_in
    )


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    history_id: UUID,
):
    player_team_history_service.delete(db=db, history_id=history_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
