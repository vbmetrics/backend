import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import Boolean, Column, DateTime, String, func, text
from sqlalchemy import Enum as SA_Enum
from sqlmodel import Field, SQLModel

# ZMIANA: Import z core zamiast definicji lokalnej
from app.core.enums import UserRole


class UserBase(SQLModel):
    email: EmailStr = Field(index=True, unique=True) # Warto dodać unique=True dla bazy
    full_name: Optional[str] = None
    role: UserRole = Field(
        sa_column=Column(SA_Enum(UserRole), nullable=False, server_default="user")
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    is_superuser: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))

    # Timestamps
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
