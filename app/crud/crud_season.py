from collections.abc import Sequence
from datetime import date
from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Season, SeasonType
from app.schemas import SeasonCreateDTO, SeasonUpdateDTO


class CRUDSeason(CRUDBase[Season, SeasonCreateDTO, SeasonUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Season | None:
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_by_name(self, db: Session, name: str) -> Season | None:
        statement = select(self.model).where(self.model.name == name)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        season_type: SeasonType | None = None,
        active_on: date | None = None,  # seasons active on this date
        date_from: date | None = None,  # seasons starting on/after
        date_to: date | None = None,  # seasons ending on/before
        search: str | None = None,  # search by name
    ) -> Sequence[Season]:
        statement = select(self.model)

        # mypy-safe columns
        name_col: Any = self.model.name
        type_col: Any = self.model.season_type
        start_col: Any = self.model.start_date
        end_col: Any = self.model.end_date
        created_col: Any = self.model.created_at

        if season_type:
            statement = statement.where(type_col == season_type)
        if active_on:
            statement = statement.where(start_col <= active_on).where(
                end_col >= active_on
            )
        if date_from:
            statement = statement.where(start_col >= date_from)
        if date_to:
            statement = statement.where(end_col <= date_to)
        if search:
            ilike = f"%{search}%"
            statement = statement.where(name_col.ilike(ilike))  # type: ignore[attr-defined]

        statement = (
            statement.order_by(start_col.desc(), created_col.desc())
            .offset(skip)
            .limit(limit)
        )
        return cast(Sequence[Season], db.exec(statement).all())


season = CRUDSeason(Season)
