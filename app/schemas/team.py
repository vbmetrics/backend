from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from app.models.team import TeamType


class TeamBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=255)
    team_type: TeamType
    logo_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None
    country_code: str = Field(min_length=2, max_length=2)
    home_arena_id: Optional[UUID] = None


class TeamCreateDTO(TeamBaseDTO):
    """Payload to create Team."""


class TeamUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    team_type: Optional[TeamType] = None
    logo_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)
    home_arena_id: Optional[UUID] = None


class TeamReadDTO(TeamBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
