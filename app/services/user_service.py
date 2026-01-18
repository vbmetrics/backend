from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.core.security import get_password_hash
from app.crud.crud_user import user as user_crud
from app.models.user import User

# ZMIANA: Importujemy oba DTO do tworzenia
from app.schemas.user import UserCreateDTO, UserRegisterDTO, UserUpdateDTO
from app.services.errors import ConflictError, NotFoundError


class UserService:
    def __init__(self):
        self.user_crud = user_crud

    def get_by_id(self, db: Session, user_id: UUID) -> User:
        obj = self.user_crud.get(db=db, id=user_id)
        if not obj:
            raise NotFoundError(
                "User not found",
                code="USER_NOT_FOUND",
                details={"user_id": str(user_id)},
            )
        return obj

    def get_by_email(self, db: Session, email: str) -> User | None:
        return self.user_crud.get_by_email(db=db, email=email)

    def get_all(
        self, db: Session, *, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> Sequence[User]:
        return self.user_crud.get_multi(db=db, skip=skip, limit=limit, search=search)

    # ZMIANA: Obsługa UserCreateDTO ORAZ UserRegisterDTO
    def create(self, db: Session, body: UserCreateDTO | UserRegisterDTO) -> User:
        if self.user_crud.get_by_email(db, body.email):
            raise ConflictError(
                "Email already in use",
                code="EMAIL_TAKEN",
                details={"email": body.email},
            )

        # 1. Zamieniamy DTO na dict (bezpieczniejsze przy transformacji danych)
        user_data = body.model_dump()

        # 2. Wyciągamy czyste hasło i haszujemy je
        plain_password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(plain_password)

        # 3. Przekazujemy słownik do CRUD
        # (CRUDBase zazwyczaj obsługuje dict jako obj_in)
        created: User = self.user_crud.create(db=db, obj_in=user_data)
        return created

    def update(self, db: Session, user_id: UUID, body: UserUpdateDTO) -> User:
        obj = self.get_by_id(db=db, user_id=user_id)

        # exclude_unset=True jest kluczowe dla PATCH
        # (aktualizujemy tylko to, co przesłano)
        data = body.model_dump(exclude_unset=True)

        if "password" in data and data["password"]:
            data["hashed_password"] = get_password_hash(data.pop("password"))

        updated: User = self.user_crud.update(db=db, db_obj=obj, obj_in=data)
        return updated

    def delete(self, db: Session, user_id: UUID) -> User:
        obj = self.get_by_id(db=db, user_id=user_id)
        removed: User = self.user_crud.remove(db=db, db_obj=obj)
        return removed
