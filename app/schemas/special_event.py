from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.special_event import SpecialEventType


class SpecialEventBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_type: SpecialEventType
    raw_special_code: str = Field(min_length=1, max_length=128)

    match_id: UUID
    set_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    player_id: Optional[UUID] = None

    occurred_at: Optional[datetime] = None
    details: Optional[dict[str, Any]] = None


class SpecialEventCreateDTO(SpecialEventBaseDTO):
    """Payload to create SpecialEvent."""


class SpecialEventUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_type: Optional[SpecialEventType] = None
    raw_special_code: Optional[str] = Field(default=None, min_length=1, max_length=128)

    set_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    player_id: Optional[UUID] = None

    occurred_at: Optional[datetime] = None
    details: Optional[dict[str, Any]] = None


class SpecialEventReadDTO(SpecialEventBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
