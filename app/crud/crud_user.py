from collections.abc import Sequence
from typing import cast
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.user import User

# ZMIANA: Importujemy też UserRegisterDTO, jeśli będziemy go używać,
# lub po prostu polegamy na tym, że CRUD przyjmuje dict lub odpowiedni model.
from app.schemas.user import UserCreateDTO, UserRegisterDTO, UserUpdateDTO


# CRUDUser dziedziczy teraz unię typów dla create_schema, aby obsłużyć oba przypadki
class CRUDUser(CRUDBase[User, UserCreateDTO | UserRegisterDTO, UserUpdateDTO]):

    def get(self, db: Session, id: UUID) -> User | None:
        return db.exec(select(self.model).where(self.model.id == id)).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.exec(select(self.model).where(self.model.email == email)).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> Sequence[User]:
        stmt = select(self.model)
        if search:
            # Upewnij się, że pole email w modelu UserBase ma typ, który SQLModel
            # rozpoznaje jako str dla .ilike
            stmt = stmt.where(self.model.email.ilike(f"%{search}%"))  # type: ignore
        stmt = stmt.offset(skip).limit(limit)
        return cast(Sequence[User], db.exec(stmt).all())

user = CRUDUser(User)
