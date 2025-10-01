from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_arena import CRUDArena
from app.models.arena import Arena
from app.schemas import ArenaCreateDTO, ArenaUpdateDTO
from app.services.errors import BadRequestError, NotFoundError


class ArenaService:
    def __init__(self, arena_crud: CRUDArena):
        """
        Service to manage arenas.

        :param arena_crud: CRUD object to interact with database.
        """
        self.arena_crud = arena_crud

    def get_by_id(self, db: Session, arena_id: UUID) -> Arena:
        db_arena = self.arena_crud.get(db=db, id=arena_id)
        if not db_arena:
            raise NotFoundError(
                "Arena not found",
                code="ARENA_NOT_FOUND",
                details={"arena_id": str(arena_id)},
            )
        return db_arena

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        country_code: str | None = None,
        city: str | None = None,
        search: str | None = None,
    ) -> Sequence[Arena]:
        return self.arena_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            country_code=country_code,
            city=city,
            search=search,
        )

    def create(self, db: Session, arena_in: ArenaCreateDTO) -> Arena:
        if len(arena_in.country_code) != 2:
            raise BadRequestError(
                "country_code must be 2 letters", code="INVALID_COUNTRY_CODE"
            )
        return self.arena_crud.create(db=db, obj_in=arena_in)

    def update(self, db: Session, arena_id: UUID, arena_in: ArenaUpdateDTO) -> Arena:
        db_arena = self.get_by_id(db=db, arena_id=arena_id)
        return self.arena_crud.update(db=db, db_obj=db_arena, obj_in=arena_in)

    def delete(self, db: Session, arena_id: UUID) -> Arena:
        db_arena = self.get_by_id(db=db, arena_id=arena_id)
        return self.arena_crud.remove(db=db, db_obj=db_arena)
