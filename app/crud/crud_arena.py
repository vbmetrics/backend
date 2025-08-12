from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_arena(session: Session, arena_id: UUID) -> models.Arena | None:
    statement = (
        select(models.Arena)
        .where(models.Arena.id == arena_id)
        .options(selectinload(models.Arena.country))  # type: ignore[arg-type]
    )
    return session.exec(statement).first()


def get_arenas(
    session: Session, skip: int = 0, limit: int = 100
) -> Sequence[models.Arena]:
    statement = select(models.Arena).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_arena(session: Session, arena: models.ArenaCreate) -> models.Arena:
    db_arena = models.Arena.model_validate(arena)
    session.add(db_arena)
    session.commit()
    session.refresh(db_arena)
    return db_arena


def update_arena(
    session: Session, db_arena: models.Arena, arena_update: models.ArenaUpdate
) -> models.Arena:
    update_data = arena_update.model_dump(exclude_unset=True)
    db_arena.sqlmodel_update(update_data)

    session.add(db_arena)
    session.commit()
    session.refresh(db_arena)
    return db_arena


def delete_arena(session: Session, db_arena: models.Arena) -> None:
    session.delete(db_arena)
    session.commit()
    return
