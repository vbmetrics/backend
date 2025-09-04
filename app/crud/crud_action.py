from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Action, ActionCreate, ActionUpdate


class CRUDAction(CRUDBase[Action, ActionCreate, ActionUpdate]):
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
        db,
        *,
        skip=0,
        limit=100,
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
                cast(ColumnElement[Any], self.model.rally_id),  # TODO: fix models
                self.model.sequence_in_rally.asc(),  # type: ignore
            )

        if rally_id:
            statement = statement.where(self.model.rally_id == rally_id)

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
        # TODO: same cast method in other crud files ?
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
