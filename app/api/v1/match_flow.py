# app/api/v1/match_flow.py
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api import deps
from app.schemas.lineup import LineupCreateDTO
from app.schemas.rally import RallyCreateDTO
from app.schemas.state import MatchStateDTO
from app.services.match_flow_service import MatchFlowService

router = APIRouter(
    prefix="/match",
    tags=["Match Flow"],
)


@router.post(
    "/{match_id}/lineup",
    response_model=MatchStateDTO,
    status_code=status.HTTP_201_CREATED,
)
def set_initial_lineup_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    payload: LineupCreateDTO,
    service: MatchFlowService = Depends(deps.get_match_flow_service),
):
    return service.apply_initial_lineup(db=db, match_id=match_id, dto=payload)


@router.get("/{match_id}/state", response_model=MatchStateDTO)
def get_match_state_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    service: MatchFlowService = Depends(deps.get_match_flow_service),
):
    return service.get_state(db=db, match_id=match_id)


@router.post(
    "/{match_id}/rally",
    response_model=MatchStateDTO,
    status_code=status.HTTP_201_CREATED,
)
def append_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    payload: RallyCreateDTO,
    service: MatchFlowService = Depends(deps.get_match_flow_service),
):
    return service.add_rally_from_code(db=db, match_id=match_id, code=payload.code)


@router.get("/{match_id}/rallies?limit={limit}")
def get_rallies_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    limit: int = 10,
    service: MatchFlowService = Depends(deps.get_match_service),
):
    # TODO
    return  # service.get_rallies(db=db, match_id=match_id, limit=limit)
