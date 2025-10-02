from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.schemas import (
    StaffTeamHistoryCreateDTO,
    StaffTeamHistoryReadDTO,
    StaffTeamHistoryUpdateDTO,
)
from app.services.staff_team_history_service import StaffTeamHistoryService

router = APIRouter(
    prefix="/staff-team-history",
    tags=["Staff-Team History"],
)


@router.post(
    "/", response_model=StaffTeamHistoryReadDTO, status_code=status.HTTP_201_CREATED
)
def create_staff_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    sth_in: StaffTeamHistoryCreateDTO,
    service: StaffTeamHistoryService = Depends(deps.get_staff_team_history_service),
):
    return service.create(db=db, sth_in=sth_in)


@router.get("/", response_model=list[StaffTeamHistoryReadDTO])
def read_staff_team_histories_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    staff_member_id: UUID | None = None,
    team_id: UUID | None = None,
    season_id: UUID | None = None,
    service: StaffTeamHistoryService = Depends(deps.get_staff_team_history_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        staff_member_id=staff_member_id,
        team_id=team_id,
        season_id=season_id,
    )


@router.get("/{sth_id}", response_model=StaffTeamHistoryReadDTO)
def read_staff_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    sth_id: UUID,
    service: StaffTeamHistoryService = Depends(deps.get_staff_team_history_service),
):
    return service.get_by_id(db=db, sth_id=sth_id)


@router.patch("/{sth_id}", response_model=StaffTeamHistoryReadDTO)
def update_staff_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    sth_id: UUID,
    sth_in: StaffTeamHistoryUpdateDTO,
    service: StaffTeamHistoryService = Depends(deps.get_staff_team_history_service),
):
    return service.update(db=db, sth_id=sth_id, sth_in=sth_in)


@router.delete("/{sth_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_team_history_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    sth_id: UUID,
    service: StaffTeamHistoryService = Depends(deps.get_staff_team_history_service),
):
    service.delete(db=db, sth_id=sth_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
