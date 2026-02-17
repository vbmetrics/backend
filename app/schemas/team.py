from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.team import TeamType


class TeamBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=255)
    team_type: TeamType

    # ZMIANA: Zastąpienie HttpUrl zwykłym str
    logo_url: Optional[str] = Field(default=None, max_length=2048)
    website_url: Optional[str] = Field(default=None, max_length=2048)

    email: Optional[EmailStr] = None
    country_code: str = Field(min_length=2, max_length=2)
    home_arena_id: Optional[UUID] = None


class TeamCreateDTO(TeamBaseDTO):
    """Payload to create Team."""


class TeamUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    team_type: Optional[TeamType] = None

    # ZMIANA
    logo_url: Optional[str] = Field(default=None, max_length=2048)
    website_url: Optional[str] = Field(default=None, max_length=2048)

    email: Optional[EmailStr] = None
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)
    home_arena_id: Optional[UUID] = None


class TeamReadDTO(TeamBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
