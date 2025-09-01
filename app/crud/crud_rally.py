from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Rally, RallyCreate, RallyUpdate


class CRUDRally(CRUDBase[Rally, RallyCreate, RallyUpdate]):
    def get(self, db: Session, id: UUID) -> Rally | None:
        """
        Overwrites get method to add eager loading for relationships.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.set),  # type: ignore[arg-type]
                selectinload(self.model.serve_team),  # type: ignore[arg-type]
                selectinload(self.model.score_team),  # type: ignore[arg-type]
            )
        )
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
    ) -> Sequence[Rally]:
        """
        Overwrites get_multi method to add dynamic filters.
        """
        statement = select(self.model).order_by(
            self.model.rally_number_in_set.desc()  # type: ignore
        )

        if set_id:
            statement = statement.where(self.model.set_id == set_id)

        if serve_team_id:
            statement = statement.where(self.model.serve_team_id == serve_team_id)

        if score_team_id:
            statement = statement.where(self.model.score_team_id == score_team_id)

        statement = (
            statement.offset(skip)
            .limit(limit)
            .options(
                selectinload(self.model.set),  # type: ignore[arg-type]
                selectinload(self.model.serve_team),  # type: ignore[arg-type]
                selectinload(self.model.score_team),  # type: ignore[arg-type]
            )
        )
        return db.exec(statement).all()

    def get_by_set_id_and_rally_number(
        self, db: Session, *, set_id: UUID, rally_number: int
    ) -> Rally | None:
        statement = select(self.model).where(
            self.model.set_id == set_id,
            self.model.rally_number_in_set == rally_number,
        )
        return db.exec(statement).first()


rally = CRUDRally(Rally)
