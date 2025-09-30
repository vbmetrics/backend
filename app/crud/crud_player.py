from collections.abc import Sequence
from typing import cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.player import Player, PlayerPosition
from app.schemas import PlayerCreateDTO, PlayerUpdateDTO


class CRUDPlayer(CRUDBase[Player, PlayerCreateDTO, PlayerUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Player | None:
        """
        Overwrites get method to add eager loading for 'nationality' relationship.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        nationality_code: str | None = None,
        playing_position: PlayerPosition | None = None,
        search: str | None = None,
    ) -> Sequence[Player]:
        statement = select(self.model)

        if nationality_code:
            statement = statement.where(self.model.nationality_code == nationality_code)
        if playing_position:
            statement = statement.where(self.model.playing_position == playing_position)
        if search:
            ilike = f"%{search}%"
            # SQLModel on Postgres: .ilike is available via SQLAlchemy
            statement = statement.where(
                (self.model.first_name.ilike(ilike))  # type: ignore[attr-defined]
                | (self.model.last_name.ilike(ilike))  # type: ignore[attr-defined]
            )

        statement = (
            statement.order_by(self.model.last_name, self.model.first_name)
            .offset(skip)
            .limit(limit)
        )
        return cast(Sequence[Player], db.exec(statement).all())

    def get_by_name(
        self, db: Session, first_name: str, last_name: str
    ) -> Player | None:
        statement = select(self.model).where(
            self.model.first_name == first_name,
            self.model.last_name == last_name,
        )
        return db.exec(statement).first()


player = CRUDPlayer(Player)
