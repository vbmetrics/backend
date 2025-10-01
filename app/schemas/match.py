from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MatchBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_date: Optional[date] = None
    spectators: Optional[int] = Field(default=None, ge=0)
    home_team_score: Optional[int] = Field(default=None, ge=0)
    away_team_score: Optional[int] = Field(default=None, ge=0)

    season_id: UUID
    home_team_id: UUID
    away_team_id: UUID
    winner_team_id: Optional[UUID] = None
    arena_id: Optional[UUID] = None


class MatchCreateDTO(MatchBaseDTO):
    """Payload to create Match."""


class MatchUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_date: Optional[date] = None
    spectators: Optional[int] = Field(default=None, ge=0)
    home_team_score: Optional[int] = Field(default=None, ge=0)
    away_team_score: Optional[int] = Field(default=None, ge=0)

    season_id: Optional[UUID] = None
    home_team_id: Optional[UUID] = None
    away_team_id: Optional[UUID] = None
    winner_team_id: Optional[UUID] = None
    arena_id: Optional[UUID] = None


class MatchReadDTO(MatchBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
