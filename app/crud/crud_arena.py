from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import or_
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.arena import Arena
from app.schemas import ArenaCreateDTO, ArenaUpdateDTO


class CRUDArena(CRUDBase[Arena, ArenaCreateDTO, ArenaUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Arena | None:
        """
        Overwrites get method to add eager loading for 'country' relationship.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        country_code: str | None = None,
        city: str | None = None,
        search: str | None = None,
    ) -> Sequence[Arena]:
        statement = select(self.model)

        if country_code:
            statement = statement.where(self.model.country_code == country_code)
        if city:
            statement = statement.where(self.model.city == city)

        if search:
            ilike = f"%{search}%"
            # Cast SQLModel columns to Any so mypy doesn't treat them as `str | None`
            name_col: Any = self.model.name
            city_col: Any = self.model.city
            addr_col: Any = self.model.address
            statement = statement.where(
                or_(
                    name_col.ilike(ilike),
                    city_col.ilike(ilike),
                    addr_col.ilike(ilike),
                )
            )

        statement = statement.order_by(self.model.name).offset(skip).limit(limit)
        return cast(Sequence[Arena], db.exec(statement).all())

    def get_by_name(self, db: Session, name: str) -> Arena | None:
        """
        Get an arena by its name.
        """
        statement = select(self.model).where(self.model.name == name)
        return db.exec(statement).first()


arena = CRUDArena(Arena)
