from collections.abc import Sequence
from typing import cast
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.action import Action
from app.schemas import ActionCreateDTO, ActionUpdateDTO


class CRUDAction(CRUDBase[Action, ActionCreateDTO, ActionUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Action | None:
        """
        Overwrites get method to add eager loading for relationships.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.rally),  # type: ignore[arg-type]
                selectinload(self.model.player),  # type: ignore[arg-type]
            )
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        rally_id: UUID | None = None,
        player_id: UUID | None = None,
    ) -> Sequence[Action]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model)
        if rally_id:
            statement = statement.where(self.model.rally_id == rally_id).order_by(
                self.model.sequence_in_rally.asc()  # type: ignore
            )
        else:
            statement = statement.order_by(
                self.model.rally_id,  # type: ignore
                self.model.sequence_in_rally.asc(),  # type: ignore
            )

        if player_id:
            statement = statement.where(self.model.player_id == player_id)

        statement = (
            statement.offset(skip)
            .limit(limit)
            .options(
                selectinload(self.model.rally),  # type: ignore[arg-type]
                selectinload(self.model.player),  # type: ignore[arg-type]
            )
        )

        return cast(Sequence[Action], db.exec(statement).all())

    def get_by_rally_id_and_sequence(
        self, db: Session, *, rally_id: UUID, sequence: int
    ) -> Action | None:
        statement = select(self.model).where(
            self.model.rally_id == rally_id,
            self.model.sequence_in_rally == sequence,
        )
        return db.exec(statement).first()


action = CRUDAction(Action)
