from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PlayerTeamHistoryBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_date: date
    end_date: Optional[date] = None
    jersey_number: Optional[int] = Field(default=None, gt=0)

    player_id: UUID
    team_id: UUID
    season_id: UUID

    @model_validator(mode="after")
    def _check_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self


class PlayerTeamHistoryCreateDTO(PlayerTeamHistoryBaseDTO):
    """Payload to create PlayerTeamHistory."""


class PlayerTeamHistoryUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    jersey_number: Optional[int] = Field(default=None, gt=0)

    player_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    season_id: Optional[UUID] = None


class PlayerTeamHistoryReadDTO(PlayerTeamHistoryBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
