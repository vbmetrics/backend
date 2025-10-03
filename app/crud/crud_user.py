from collections.abc import Sequence
from typing import cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreateDTO, UserUpdateDTO


class CRUDUser(CRUDBase[User, UserCreateDTO, UserUpdateDTO]):
    def get(self, db: Session, id: UUID) -> User | None:
        stmt = select(self.model).where(self.model.id == id)
        return db.exec(stmt).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(self.model).where(self.model.email == email)
        return db.exec(stmt).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> Sequence[User]:
        stmt = select(self.model)
        if search:
            stmt = stmt.where(self.model.email.ilike(f"%{search}%"))  # type: ignore[attr-defined]
        stmt = stmt.offset(skip).limit(limit)
        return cast(Sequence[User], db.exec(stmt).all())


user = CRUDUser(User)
