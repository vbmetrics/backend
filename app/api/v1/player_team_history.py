from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from .. import models
from ..crud import crud
from ..db.database import get_session

router = APIRouter(
    prefix="/player-team-history",
    tags=["Player-Team History"],
)


@router.post(
    "/",
    response_model=models.PlayerTeamHistoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_player_team_history(
    history: models.PlayerTeamHistoryCreate, session: Session = Depends(get_session)
):
    return crud.create_player_team_history(session=session, history=history)


@router.get("/", response_model=list[models.PlayerTeamHistoryReadWithDetails])
def read_player_team_histories(
    skip: int = 0,
    limit: int = 100,
    player_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    season_id: Optional[UUID] = None,
    session: Session = Depends(get_session),
):
    histories = crud.get_player_team_histories(
        session=session,
        skip=skip,
        limit=limit,
        player_id=player_id,
        team_id=team_id,
        season_id=season_id,
    )
    return histories


@router.get("/{history_id}", response_model=models.PlayerTeamHistoryReadWithDetails)
def read_player_team_history(history_id: UUID, session: Session = Depends(get_session)):
    db_history = crud.get_player_team_history(session=session, history_id=history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="History record not found")
    return db_history


@router.patch("/{history_id}", response_model=models.PlayerTeamHistoryRead)
def update_player_team_history(
    history_id: UUID,
    history_update: models.PlayerTeamHistoryUpdate,
    session: Session = Depends(get_session),
):
    db_history = session.get(models.PlayerTeamHistory, history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="History record not found")

    return crud.update_player_team_history(
        session=session, db_history=db_history, history_update=history_update
    )
