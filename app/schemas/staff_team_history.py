from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StaffTeamHistoryBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str = Field(min_length=1, max_length=100)
    staff_member_id: UUID
    team_id: UUID
    season_id: UUID


class StaffTeamHistoryCreateDTO(StaffTeamHistoryBaseDTO):
    """Payload to create StaffTeamHistory."""


class StaffTeamHistoryUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: Optional[str] = Field(default=None, min_length=1, max_length=100)


class StaffTeamHistoryReadDTO(StaffTeamHistoryBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
