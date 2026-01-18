# app/api/v1/live.py
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Response, status
from sqlmodel import Session

from app.api import deps
from app.schemas.live import LineupDTO, MatchStateDTO, RallyCreateDTO
from app.services.live_service import LiveService

router = APIRouter(prefix="/match", tags=["Live"])


@router.post("/{match_id}/lineup", status_code=status.HTTP_204_NO_CONTENT)
def set_lineup(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    payload: LineupDTO,
    service: LiveService = Depends(deps.get_live_service),
):
    service.set_lineup(db=db, match_id=match_id, payload=payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{match_id}/rally", response_model=MatchStateDTO)
def add_rally(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    payload: RallyCreateDTO,
    service: LiveService = Depends(deps.get_live_service),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    return service.add_rally(
        db=db,
        match_id=match_id,
        code=payload.code,
        comment=payload.comment,
        idempotency_key=idempotency_key,
    )


@router.get("/{match_id}/state", response_model=MatchStateDTO)
def get_state(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    limit: int = 10,
    service: LiveService = Depends(deps.get_live_service),
):
    return service.get_state(db=db, match_id=match_id, last=limit)
