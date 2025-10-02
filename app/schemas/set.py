from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SetBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    set_number: int = Field(gt=0, description="Set number in match (1, 2, 3, etc.)")
    home_team_score: int = Field(default=0, ge=0)
    away_team_score: int = Field(default=0, ge=0)
    duration_minutes: Optional[int] = Field(default=None, ge=0)

    match_id: UUID
    winner_team_id: Optional[UUID] = None


class SetCreateDTO(SetBaseDTO):
    """Payload to create Set."""


class SetUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    home_team_score: Optional[int] = Field(default=None, ge=0)
    away_team_score: Optional[int] = Field(default=None, ge=0)
    winner_team_id: Optional[UUID] = None
    duration_minutes: Optional[int] = Field(default=None, ge=0)


class SetReadDTO(SetBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
