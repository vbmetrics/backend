from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api import deps
from app.schemas.lineup import LineupCreateDTO, LineupReadDTO
from app.services.lineup_service import LineupService

router = APIRouter(prefix="/lineup", tags=["Lineup"])


@router.post(
    "/set/{set_id}/bulk",
    response_model=list[LineupReadDTO],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.get_current_active_user)],
)
def create_set_lineups_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_id: UUID,
    payload: LineupCreateDTO,
    service: LineupService = Depends(deps.get_lineup_service),
):
    return service.create_set_lineups(db=db, set_id=set_id, payload=payload)
