from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.rally import Rally
from app.schemas import RallyCreateDTO, RallyUpdateDTO


class CRUDRally(CRUDBase[Rally, RallyCreateDTO, RallyUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Rally | None:
        """
        Overwrites get method to add eager loading for relationships.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        set_id: UUID | None = None,
        serve_team_id: UUID | None = None,
        score_team_id: UUID | None = None,
        rally_number_from: int | None = None,
        rally_number_to: int | None = None,
    ) -> Sequence[Rally]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model)

        # mypy-safe casts for operators on SQL columns
        set_col: Any = self.model.set_id
        serve_col: Any = self.model.serve_team_id
        score_col: Any = self.model.score_team_id
        num_col: Any = self.model.rally_number_in_set
        created_col: Any = self.model.created_at

        if set_id:
            statement = statement.where(set_col == set_id)
        if serve_team_id:
            statement = statement.where(serve_col == serve_team_id)
        if score_team_id:
            statement = statement.where(score_col == score_team_id)
        if rally_number_from is not None:
            statement = statement.where(num_col >= rally_number_from)
        if rally_number_to is not None:
            statement = statement.where(num_col <= rally_number_to)

        statement = statement.order_by(num_col, created_col).offset(skip).limit(limit)
        return cast(Sequence[Rally], db.exec(statement).all())

    def get_by_set_id_and_rally_number(
        self, db: Session, *, set_id: UUID, rally_number_in_set: int
    ) -> Rally | None:
        statement = select(self.model).where(
            self.model.set_id == set_id,
            self.model.rally_number_in_set == rally_number_in_set,
        )
        return db.exec(statement).first()


rally = CRUDRally(Rally)
