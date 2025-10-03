import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, String, func
from sqlmodel import Field, SQLModel


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    jti: str = Field(
        sa_column=Column(String(128), unique=True, index=True, nullable=False)
    )
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    # optional device / client hint
    user_agent: Optional[str] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)

    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    revoked_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    def is_active(self, now: datetime) -> bool:
        return self.revoked_at is None and now < self.expires_at
