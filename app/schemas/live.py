from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PositionsDTO(BaseModel):
    P1: UUID
    P2: UUID
    P3: UUID
    P4: UUID
    P5: UUID
    P6: UUID


class LineupSideDTO(BaseModel):
    team_id: UUID
    positions: PositionsDTO
    libero_id: Optional[UUID] = None


class LineupDTO(BaseModel):
    home: LineupSideDTO
    away: LineupSideDTO
    starting_server: Literal["home", "away"]


class RallyCreateDTO(BaseModel):
    code: str = Field(min_length=2, max_length=1024)
    comment: Optional[str] = None


class RallySummaryDTO(BaseModel):
    id: UUID
    code: str
    winner: Literal["home", "away"]
    score: str


class MatchStateDTO(BaseModel):
    match_id: UUID
    set_number: int
    home_sets: int
    away_sets: int
    home_points: int
    away_points: int
    serving_team_id: UUID
    rotation_home: list[UUID]
    rotation_away: list[UUID]
    last_rallies: list[RallySummaryDTO]
