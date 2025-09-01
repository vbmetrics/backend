from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Set, SetCreate, SetUpdate


class CRUDSet(CRUDBase[Set, SetCreate, SetUpdate]):
    def get(self, db: Session, id: UUID) -> Set | None:
        """
        Overwrites get method to add eager loading for relationships.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.match),  # type: ignore[arg-type]
                selectinload(self.model.winner_team),  # type: ignore[arg-type]
            )
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
    ) -> Sequence[Set]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model).order_by(self.model.set_number.desc())  # type: ignore

        if match_id:
            statement = statement.where(self.model.match_id == match_id)

        if winner_team_id:
            statement = statement.where(self.model.winner_team_id == winner_team_id)

        statement = (
            statement.offset(skip)
            .limit(limit)
            .options(
                selectinload(self.model.match),  # type: ignore[arg-type]
                selectinload(self.model.winner_team),  # type: ignore[arg-type]
            )
        )
        return db.exec(statement).all()

    def get_by_match_id_and_set_number(
        self,
        db: Session,
        *,
        match_id: UUID,
        set_number: int,
    ) -> Set | None:
        statement = select(self.model).where(
            self.model.match_id == match_id, self.model.set_number == set_number
        )
        return db.exec(statement).first()


set = CRUDSet(Set)
