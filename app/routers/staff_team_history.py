from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from .. import crud, models
from ..database import get_session

router = APIRouter(
    prefix="/staff-team-history",
    tags=["Staff-Team History"],
)


@router.post(
    "/", response_model=models.StaffTeamHistoryRead, status_code=status.HTTP_201_CREATED
)
def create_staff_team_history(
    history: models.StaffTeamHistoryCreate, session: Session = Depends(get_session)
):
    return crud.create_staff_team_history(session=session, history=history)


@router.get("/", response_model=list[models.StaffTeamHistoryRead])
def read_staff_team_histories(
    skip: int = 0,
    limit: int = 100,
    staff_member_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    season_id: Optional[UUID] = None,
    session: Session = Depends(get_session),
):
    return crud.get_staff_team_histories(
        session=session,
        skip=skip,
        limit=limit,
        staff_member_id=staff_member_id,
        team_id=team_id,
        season_id=season_id,
    )


@router.get("/{history_id}", response_model=models.StaffTeamHistoryReadWithDetails)
def read_staff_team_history(history_id: UUID, session: Session = Depends(get_session)):
    db_history = crud.get_staff_team_history(session=session, history_id=history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="History record not found")
    return db_history
