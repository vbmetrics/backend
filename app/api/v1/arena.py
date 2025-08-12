from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from .. import models
from ..crud import crud
from ..db.database import get_session

router = APIRouter(
    prefix="/arenas",
    tags=["Arenas"],
)


@router.post("/", response_model=models.ArenaRead, status_code=status.HTTP_201_CREATED)
def create_arena(arena: models.ArenaCreate, session: Session = Depends(get_session)):
    return crud.create_arena(session=session, arena=arena)


@router.get("/", response_model=list[models.ArenaRead])
def read_arenas(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return crud.get_arenas(session=session, skip=skip, limit=limit)


@router.get("/{arena_id}", response_model=models.ArenaReadWithCountry)
def read_arena(arena_id: UUID, session: Session = Depends(get_session)):
    db_arena = crud.get_arena(session=session, arena_id=arena_id)
    if db_arena is None:
        raise HTTPException(status_code=404, detail="Arena not found")
    return db_arena


@router.patch("/{arena_id}", response_model=models.ArenaRead)
def update_arena(
    arena_id: UUID,
    arena_update: models.ArenaUpdate,
    session: Session = Depends(get_session),
):
    db_arena = session.get(models.Arena, arena_id)
    if db_arena is None:
        raise HTTPException(status_code=404, detail="Arena not found")

    return crud.update_arena(
        session=session, db_arena=db_arena, arena_update=arena_update
    )


@router.delete("/{arena_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arena(arena_id: UUID, session: Session = Depends(get_session)):
    db_arena = session.get(models.Arena, arena_id)
    if db_arena is None:
        raise HTTPException(status_code=404, detail="Arena not found")

    crud.delete_arena(session=session, db_arena=db_arena)
    return
