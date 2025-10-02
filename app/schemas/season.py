from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.season import SeasonType


class SeasonBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=128)
    season_type: SeasonType
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def _check_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self


class SeasonCreateDTO(SeasonBaseDTO):
    """Payload to create Season."""


class SeasonUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    season_type: Optional[SeasonType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def _check_dates(self):
        # Only validate when both provided in the patch body
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot be earlier than start_date")
        return self


class SeasonReadDTO(SeasonBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
