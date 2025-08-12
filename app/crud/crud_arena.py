from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Arena, ArenaCreate, ArenaUpdate


class CRUDArena(CRUDBase[Arena, ArenaCreate, ArenaUpdate]):
    def get(self, db: Session, id: UUID) -> Arena | None:
        """
        Overwrites get method to add eager loading for 'country' relationship.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.country))  # type: ignore[arg-type]
        )
        return db.exec(statement).first()


arena = CRUDArena(Arena)
