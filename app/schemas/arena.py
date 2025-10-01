from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ArenaBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=255)
    city: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, max_length=512)
    capacity: Optional[int] = Field(default=None, gt=0)
    country_code: str = Field(
        min_length=2, max_length=2, description="ISO alpha-2 code"
    )


class ArenaCreateDTO(ArenaBaseDTO):
    """Payload to create Arena."""


class ArenaUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    city: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, max_length=512)
    capacity: Optional[int] = Field(default=None, gt=0)
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)


class ArenaReadDTO(ArenaBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
