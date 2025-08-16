import uuid
from typing import Optional
from uuid import UUID

from pydantic import field_validator
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

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Password must have at least 12 characters.")
        if len(v) > 64:
            raise ValueError("Password cannot be longer than 64 characters.")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must include at least one digit.")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must include at least one upper letter.")

        return v


class UserRead(UserBase):
    id: UUID


class UserUpdate(SQLModel):
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
