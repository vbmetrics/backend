from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_arena import CRUDArena


class ArenaService:
    def __init__(self, arena_crud: CRUDArena):
        """
        Service to manage arenas.

        :param arena_crud: CRUD object to interact with database.
        """
        self.arena_crud = arena_crud

    def get_by_id(self, db: Session, arena_id: UUID) -> models.Arena:
        db_arena = self.arena_crud.get(db=db, id=arena_id)
        if not db_arena:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Arena not found"
            )

        return db_arena

    def get_all(self, db: Session, skip: int, limit: int) -> Sequence[models.Arena]:
        return self.arena_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, arena_in: models.ArenaCreate) -> models.Arena:
        return self.arena_crud.create(db=db, obj_in=arena_in)

    def update(
        self, db: Session, arena_id: UUID, arena_in: models.ArenaUpdate
    ) -> models.Arena:
        db_arena = self.get_by_id(db=db, arena_id=arena_id)
        return self.arena_crud.update(db=db, db_obj=db_arena, obj_in=arena_in)

    def delete(self, db: Session, arena_id: UUID) -> models.Arena:
        db_arena = self.get_by_id(db=db, arena_id=arena_id)
        return self.arena_crud.remove(db=db, db_obj=db_arena)


arena_service = ArenaService(crud.arena)
