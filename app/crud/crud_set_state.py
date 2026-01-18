from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.set_state import SetState


class CRUDSetState(CRUDBase[SetState, SetState, SetState]):
    def get_by_set_id(
        self, db: Session, *, set_id: UUID, for_update: bool = False
    ) -> Optional[SetState]:
        stmt = select(SetState).where(SetState.set_id == set_id)
        if for_update:
            stmt = stmt.with_for_update()
        return db.exec(stmt).first()

    def upsert_for_set(self, db: Session, *, set_id: UUID, data: dict) -> SetState:
        obj = self.get_by_set_id(db, set_id=set_id)
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        obj = SetState(set_id=set_id, **data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


crud_set_state = CRUDSetState(SetState)
