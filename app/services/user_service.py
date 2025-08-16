from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_user import CRUDUser


class UserService:
    def __init__(self, user_crud: CRUDUser):
        self.user_crud = user_crud

    def get_by_email(self, db: Session, *, email: str) -> models.User | None:
        return self.user_crud.get_by_email(db=db, email=email)

    def create(self, db: Session, *, user_in: models.UserCreate) -> models.User:
        db_user = self.get_by_email(db=db, email=user_in.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        return self.user_crud.create(db=db, obj_in=user_in)

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> models.User | None:
        return self.user_crud.authenticate(db=db, email=email, password=password)


user_service = UserService(crud.user)
