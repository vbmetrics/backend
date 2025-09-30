from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.player import PlayerHand, PlayerPosition


class PlayerBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date

    height_cm: Optional[int] = Field(default=None, gt=0)
    weight_kg: Optional[int] = Field(default=None, gt=0)

    playing_position: Optional[PlayerPosition] = None
    dominant_hand: Optional[PlayerHand] = None

    spike_reach_cm: Optional[int] = Field(default=None, gt=0)
    block_reach_cm: Optional[int] = Field(default=None, gt=0)

    photo_url: Optional[str] = Field(default=None, max_length=2048)
    bio: Optional[str] = None

    nationality_code: str = Field(
        min_length=2, max_length=2, description="ISO alpha-2 code of nationality"
    )


class PlayerCreateDTO(PlayerBaseDTO):
    """Payload to create Player."""


class PlayerUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None

    height_cm: Optional[int] = Field(default=None, gt=0)
    weight_kg: Optional[int] = Field(default=None, gt=0)

    playing_position: Optional[PlayerPosition] = None
    dominant_hand: Optional[PlayerHand] = None

    spike_reach_cm: Optional[int] = Field(default=None, gt=0)
    block_reach_cm: Optional[int] = Field(default=None, gt=0)

    photo_url: Optional[str] = Field(default=None, max_length=2048)
    bio: Optional[str] = None

    nationality_code: Optional[str] = Field(default=None, min_length=2, max_length=2)


class PlayerReadDTO(PlayerBaseDTO):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
