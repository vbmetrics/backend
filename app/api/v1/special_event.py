from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.special_event import SpecialEventType
from app.schemas import (
    SpecialEventCreateDTO,
    SpecialEventReadDTO,
    SpecialEventUpdateDTO,
)
from app.services.special_event_service import SpecialEventService

router = APIRouter(prefix="/special-event", tags=["SpecialEvent"])


@router.post(
    "/", response_model=SpecialEventReadDTO, status_code=status.HTTP_201_CREATED
)
def create_special_event_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    se_in: SpecialEventCreateDTO,
    service: SpecialEventService = Depends(deps.get_special_event_service),
):
    return service.create(db=db, se_in=se_in)


@router.get("/", response_model=list[SpecialEventReadDTO])
def get_special_events_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    match_id: UUID | None = None,
    set_id: UUID | None = None,
    team_id: UUID | None = None,
    player_id: UUID | None = None,
    event_type: SpecialEventType | None = None,
    occurred_from: datetime | None = None,
    occurred_to: datetime | None = None,
    search: str | None = None,
    service: SpecialEventService = Depends(deps.get_special_event_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        match_id=match_id,
        set_id=set_id,
        team_id=team_id,
        player_id=player_id,
        event_type=event_type,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        search=search,
    )


@router.get("/{se_id}", response_model=SpecialEventReadDTO)
def get_special_event_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    se_id: UUID,
    service: SpecialEventService = Depends(deps.get_special_event_service),
):
    return service.get_by_id(db=db, se_id=se_id)


@router.patch("/{se_id}", response_model=SpecialEventReadDTO)
def update_special_event_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    se_id: UUID,
    se_in: SpecialEventUpdateDTO,
    service: SpecialEventService = Depends(deps.get_special_event_service),
):
    return service.update(db=db, se_id=se_id, se_in=se_in)


@router.delete("/{se_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_special_event_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    se_id: UUID,
    service: SpecialEventService = Depends(deps.get_special_event_service),
):
    service.delete(db=db, se_id=se_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
