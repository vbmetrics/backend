from collections.abc import Sequence
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_set import CRUDSet
from app.crud.crud_set import vb_set as set_crud
from app.crud.crud_special_event import CRUDSpecialEvent
from app.crud.crud_special_event import special_event as se_crud
from app.models.special_event import SpecialEvent, SpecialEventType
from app.schemas import SpecialEventCreateDTO, SpecialEventUpdateDTO
from app.services.errors import BadRequestError, NotFoundError
from app.utils.special_event_parser import SpecialEventParser


class SpecialEventService:
    def __init__(
        self,
        special_event_crud: CRUDSpecialEvent = se_crud,
        set_crud: CRUDSet = set_crud,
        parser: Optional[SpecialEventParser] = None,
    ):
        self.se_crud = special_event_crud
        self.set_crud = set_crud
        self._parser = parser or SpecialEventParser()

    # ---- helpers ----

    def _validate_set_belongs_to_match(
        self, db: Session, *, match_id: UUID, maybe_set_id: UUID | None
    ) -> None:
        if maybe_set_id is None:
            return
        s = self.set_crud.get(db=db, id=maybe_set_id)
        if not s:
            raise BadRequestError(
                "set_id does not exist",
                code="SET_NOT_FOUND",
                details={"set_id": str(maybe_set_id)},
            )
        if s.match_id != match_id:
            raise BadRequestError(
                "set_id does not belong to provided match_id",
                code="SET_MATCH_MISMATCH",
                details={
                    "set_id": str(maybe_set_id),
                    "match_id": str(match_id),
                    "set.match_id": str(s.match_id),
                },
            )

    # ---- CRUD ----

    def get_by_id(self, db: Session, se_id: UUID) -> SpecialEvent:
        obj = self.se_crud.get(db=db, id=se_id)
        if not obj:
            raise NotFoundError(
                "Special event not found",
                code="SPECIAL_EVENT_NOT_FOUND",
                details={"id": str(se_id)},
            )
        return obj

    def get_all(
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
        search: str | None = None,
    ) -> Sequence[SpecialEvent]:
        return self.se_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            match_id=match_id,
            set_id=set_id,
            team_id=team_id,
            player_id=player_id,
            event_type=event_type,
            occurred_from=occurred_from,
            occurred_to=occurred_to,
            search=search,
        )

    def create(self, db: Session, se_in: SpecialEventCreateDTO) -> SpecialEvent:
        if not se_in.event_type or not se_in.details:
            event_type, details = self._parser.parse(se_in.raw_special_code)
            se_in = se_in.model_copy(
                update={
                    "event_type": se_in.event_type or event_type,
                    "details": se_in.details or details,
                }
            )

        self._validate_set_belongs_to_match(
            db, match_id=se_in.match_id, maybe_set_id=se_in.set_id
        )
        return self.se_crud.create(db=db, obj_in=se_in)

    def update(
        self, db: Session, se_id: UUID, se_in: SpecialEventUpdateDTO
    ) -> SpecialEvent:
        obj = self.get_by_id(db=db, se_id=se_id)
        data = se_in.model_dump(exclude_unset=True)

        if "raw_special_code" in data:
            event_type, details = self._parser.parse(data["raw_special_code"])
            data.setdefault("event_type", event_type)
            data.setdefault("details", details)

        new_set_id = data.get("set_id", obj.set_id)
        self._validate_set_belongs_to_match(
            db, match_id=obj.match_id, maybe_set_id=new_set_id
        )

        return self.se_crud.update(db=db, db_obj=obj, obj_in=data)

    def delete(self, db: Session, se_id: UUID) -> SpecialEvent:
        obj = self.get_by_id(db=db, se_id=se_id)
        return self.se_crud.remove(db=db, db_obj=obj)
