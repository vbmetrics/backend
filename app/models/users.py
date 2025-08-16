import uuid
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    hashed_password: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID


class UserUpdate(SQLModel):
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
