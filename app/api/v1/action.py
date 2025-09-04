from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services.action_service import ActionService

router = APIRouter(prefix="/action", tags=["Action"])


@router.post("/", response_model=models.ActionRead, status_code=status.HTTP_201_CREATED)
def create_action_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    service: ActionService = Depends(deps.get_action_service),
    action_in: models.ActionCreate,
):
    return service.create(db=db, action_in=action_in)


@router.get("/", response_model=list[models.ActionRead])
def read_actions_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    service: ActionService = Depends(deps.get_action_service),
    skip: int = 0,
    limit: int = 100,
    rally_id: UUID | None = None,
    player_id: UUID | None = None,
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        rally_id=rally_id,
        player_id=player_id,
    )


@router.get("/{action_id}", response_model=models.ActionRead)
def read_action_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    service: ActionService = Depends(deps.get_action_service),
    action_id: UUID,
):
    return service.get_by_id(db=db, action_id=action_id)


@router.patch("/{action_id}", response_model=models.ActionRead)
def update_action_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    service: ActionService = Depends(deps.get_action_service),
    action_id: UUID,
    action_in: models.ActionUpdate,
):
    return service.update(db=db, action_id=action_id, action_in=action_in)


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    service: ActionService = Depends(deps.get_action_service),
    action_id: UUID,
):
    service.delete(db=db, action_id=action_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
