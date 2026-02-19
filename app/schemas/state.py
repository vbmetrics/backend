from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

Side = Literal["home", "away"]


class RotationDTO(BaseModel):
    # indeks 0..5 odpowiada P1..P6 w kolejce serwisowej
    order: list[UUID]  # [player_id,...] długości 6
    libero_id: Optional[UUID] = None


class MatchStateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: UUID
    set_number: int
    home_sets: int
    away_sets: int
    home_points: int
    away_points: int
    serving_side: Side
    serving_index: int  # 0..5
    rotation_home: RotationDTO
    rotation_away: RotationDTO
    last_rallies: list[dict] = []  # uproszczone
    past_sets: list[dict] = []
