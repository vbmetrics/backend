from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import player_service

router = APIRouter(prefix="/player", tags=["Player"])


@router.get("/", response_model=models.PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_in: models.PlayerCreate,
):
    return player_service.create(db=db, player_in=player_in)


@router.get("/", response_model=list[models.PlayerRead])
def read_players_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return player_service.get_all(db=db, skip=skip, limit=limit)


@router.get("/{player_id}", response_model=models.PlayerRead)
def read_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_id: UUID,
):
    return player_service.get_by_id(db=db, player_id=player_id)


@router.patch("/{player_id}", response_model=models.PlayerRead)
def update_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_id: UUID,
    player_in: models.PlayerUpdate,
):
    return player_service.update(db=db, player_id=player_id, player_in=player_in)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_id: UUID,
):
    player_service.delete(db=db, player_id=player_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
