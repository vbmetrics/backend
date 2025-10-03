from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.core.security import get_password_hash
from app.crud.crud_user import user as user_crud
from app.models.user import User
from app.schemas.user import UserCreateDTO, UserUpdateDTO
from app.services.errors import ConflictError, NotFoundError


class UserService:
    def __init__(self):
        self.user_crud = user_crud

    def get_by_id(self, db: Session, user_id: UUID) -> User:
        obj: User | None = self.user_crud.get(db=db, id=user_id)
        if not obj:
            raise NotFoundError(
                "User not found",
                code="USER_NOT_FOUND",
                details={"user_id": str(user_id)},
            )
        return obj

    def get_by_email(self, db: Session, email: str) -> User | None:
        obj: User | None = self.user_crud.get_by_email(db=db, email=email)
        return obj

    def get_all(
        self, db: Session, *, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> Sequence[User]:
        objs: Sequence[User] = self.user_crud.get_multi(
            db=db, skip=skip, limit=limit, search=search
        )
        return objs

    def create(self, db: Session, body: UserCreateDTO) -> User:
        exists = self.user_crud.get_by_email(db, body.email)
        if exists:
            raise ConflictError(
                "Email already in use",
                code="EMAIL_TAKEN",
                details={"email": body.email},
            )
        hashed = get_password_hash(body.password)
        payload = body.model_copy(update={"hashed_password": hashed, "password": None})
        created: User = self.user_crud.create(db=db, obj_in=payload)
        return created

    def update(self, db: Session, user_id: UUID, body: UserUpdateDTO) -> User:
        obj = self.get_by_id(db=db, user_id=user_id)
        data = body.model_dump(exclude_unset=True)
        if "password" in data and data["password"]:
            data["hashed_password"] = get_password_hash(data.pop("password"))
        updated: User = self.user_crud.update(db=db, db_obj=obj, obj_in=data)
        return updated

    def delete(self, db: Session, user_id: UUID) -> User:
        obj = self.get_by_id(db=db, user_id=user_id)
        removed: User = self.user_crud.remove(db=db, db_obj=obj)
        return removed
