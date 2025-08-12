from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import arena_service

router = APIRouter(
    prefix="/arena",
    tags=["Arena"],
)


@router.post("/", response_model=models.ArenaRead, status_code=status.HTTP_201_CREATED)
def create_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_in: models.ArenaCreate,
):
    return arena_service.create(db=db, arena_in=arena_in)


@router.get("/", response_model=list[models.ArenaRead])
def read_arenas_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return arena_service.get_all(db=db, skip=skip, limit=limit)


@router.get("/{arena_id}", response_model=models.ArenaReadWithCountry)
def read_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_id: UUID,
):
    return arena_service.get_by_id(db=db, arena_id=arena_id)


@router.patch("/{arena_id}", response_model=models.ArenaRead)
def update_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_id: UUID,
    arena_in: models.ArenaUpdate,
):
    return arena_service.update(db=db, arena_id=arena_id, arena_in=arena_in)


@router.delete("/{arena_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_id: UUID,
):
    arena_service.delete(db=db, arena_id=arena_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
