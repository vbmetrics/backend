from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Position = Literal["P1", "P2", "P3", "P4", "P5", "P6"]


class LineupSideDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: UUID
    positions: dict[Position, UUID] = Field(
        ..., description="Map positions P1..P6 -> player UUID"
    )
    libero_id: Optional[UUID] = None


class LineupCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    home: LineupSideDTO
    away: LineupSideDTO
    set_number: int = Field(1, ge=1, le=5)
    # Kto serwuje i który w kolejce (0..5) – jeżeli nie podasz, wyliczymy z P1
    starting_server_side: Optional[Literal["home", "away"]] = None
    starting_server_index: Optional[int] = Field(default=None, ge=0, le=5)
