from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.set import Set
from app.schemas import SetCreateDTO, SetUpdateDTO


class CRUDSet(CRUDBase[Set, SetCreateDTO, SetUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Set | None:
        """
        Overwrites get method to add eager loading for relationships.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_by_match_and_number(
        self, db: Session, *, match_id: UUID, set_number: int
    ) -> Set | None:
        statement = select(self.model).where(
            self.model.match_id == match_id,
            self.model.set_number == set_number,
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        match_id: UUID | None = None,
        winner_team_id: UUID | None = None,
        set_number_from: int | None = None,
        set_number_to: int | None = None,
    ) -> Sequence[Set]:
        statement = select(self.model)

        # mypy-safe casts for SQL operators
        match_col: Any = self.model.match_id
        winner_col: Any = self.model.winner_team_id
        num_col: Any = self.model.set_number
        created_col: Any = self.model.created_at

        if match_id:
            statement = statement.where(match_col == match_id)
        if winner_team_id:
            statement = statement.where(winner_col == winner_team_id)
        if set_number_from is not None:
            statement = statement.where(num_col >= set_number_from)
        if set_number_to is not None:
            statement = statement.where(num_col <= set_number_to)

        statement = statement.order_by(num_col, created_col).offset(skip).limit(limit)
        return cast(Sequence[Set], db.exec(statement).all())


vb_set = CRUDSet(Set)
