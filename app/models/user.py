import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy import Enum as SA_Enum
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    coach = "coach"
    analyst = "analyst"


class UserBase(SQLModel):
    is_active: bool = True
    email: str = Field(
        sa_column=Column(String(320), unique=True, index=True, nullable=False)
    )
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.user, sa_column=Column(SA_Enum(UserRole)))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )


class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
