from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import set_service

router = APIRouter(prefix="/set", tags=["Set"])


@router.post("/", response_model=models.SetRead, status_code=status.HTTP_201_CREATED)
def create_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_in: models.SetCreate,
):
    return set_service.create(db=db, set_in=set_in)


@router.get("/", response_model=list[models.SetRead])
def read_sets_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    match_id: UUID | None = None,
    winner_team_id: UUID | None = None,
):
    return set_service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        match_id=match_id,
        winner_team_id=winner_team_id,
    )


@router.get("/{set_id}", response_model=models.SetRead)
def read_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_id: UUID,
):
    return set_service.get_by_id(db=db, set_id=set_id)


@router.patch("/{set_id}", response_model=models.SetRead)
def update_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_id: UUID,
    set_in: models.SetUpdate,
):
    return set_service.update(db=db, set_id=set_id, set_in=set_in)


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_id: UUID,
):
    set_service.delete(db=db, set_id=set_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
