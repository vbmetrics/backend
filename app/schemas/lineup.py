from typing import Literal, Optional, TypedDict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# klucze rotacji P1..P6
RotationKey = Literal["P1", "P2", "P3", "P4", "P5", "P6"]


class Positions(TypedDict):
    P1: UUID
    P2: UUID
    P3: UUID
    P4: UUID
    P5: UUID
    P6: UUID


class LineupSideDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: UUID
    positions: dict[RotationKey, UUID]
    libero_id: Optional[UUID] = None


class LineupCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    home: LineupSideDTO
    away: LineupSideDTO
    starting_server: Literal["home", "away"] = Field(
        ..., description="Who serves first"
    )
