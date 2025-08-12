from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from .. import models
from ..crud import crud
from ..db.database import get_session

router = APIRouter(
    prefix="/players",
    tags=["Players"],
)


class PlayerReadWithNationality(models.PlayerRead):
    nationality: Optional[models.CountryRead] = None


@router.post("/", response_model=models.PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(player: models.PlayerCreate, session: Session = Depends(get_session)):
    return crud.create_player(session=session, player=player)


@router.get("/", response_model=list[models.PlayerRead])
def read_players(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return crud.get_players(session=session, skip=skip, limit=limit)


@router.get("/{player_id}", response_model=PlayerReadWithNationality)
def read_player(player_id: UUID, session: Session = Depends(get_session)):
    db_player = crud.get_player(session=session, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player


@router.patch("/{player_id}", response_model=models.PlayerRead)
def update_player(
    player_id: UUID,
    player_update: models.PlayerUpdate,
    session: Session = Depends(get_session),
):
    db_player = session.get(models.Player, player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return crud.update_player(
        session=session, db_player=db_player, player_update=player_update
    )


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: UUID, session: Session = Depends(get_session)):
    db_player = session.get(models.Player, player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    crud.delete_player(session=session, db_player=db_player)
    return
