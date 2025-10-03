from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RefreshTokenCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jti: str = Field(min_length=1, max_length=128)
    user_id: UUID
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    revoked_at: Optional[datetime] = None


class RefreshTokenUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    revoked_at: Optional[datetime] = None
