from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.special_event import SpecialEvent, SpecialEventType
from app.schemas import SpecialEventCreateDTO, SpecialEventUpdateDTO


class CRUDSpecialEvent(
    CRUDBase[SpecialEvent, SpecialEventCreateDTO, SpecialEventUpdateDTO]
):
    def get(self, db: Session, id: UUID) -> SpecialEvent | None:
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        match_id: UUID | None = None,
        set_id: UUID | None = None,
        team_id: UUID | None = None,
        player_id: UUID | None = None,
        event_type: SpecialEventType | None = None,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
        search: str | None = None,  # searches raw_special_code
    ) -> Sequence[SpecialEvent]:
        statement = select(self.model)

        # mypy-safe columns
        match_col: Any = self.model.match_id
        set_col: Any = self.model.set_id
        team_col: Any = self.model.team_id
        player_col: Any = self.model.player_id
        type_col: Any = self.model.event_type
        code_col: Any = self.model.raw_special_code
        occ_col: Any = self.model.occurred_at
        created_col: Any = self.model.created_at

        if match_id:
            statement = statement.where(match_col == match_id)
        if set_id:
            statement = statement.where(set_col == set_id)
        if team_id:
            statement = statement.where(team_col == team_id)
        if player_id:
            statement = statement.where(player_col == player_id)
        if event_type:
            statement = statement.where(type_col == event_type)
        if occurred_from:
            statement = statement.where(occ_col >= occurred_from)
        if occurred_to:
            statement = statement.where(occ_col <= occurred_to)
        if search:
            statement = statement.where(code_col.ilike(f"%{search}%"))  # type: ignore[attr-defined]

        statement = statement.order_by(occ_col, created_col).offset(skip).limit(limit)
        return cast(Sequence[SpecialEvent], db.exec(statement).all())


special_event = CRUDSpecialEvent(SpecialEvent)
