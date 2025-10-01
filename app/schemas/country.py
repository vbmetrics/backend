from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CountryBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=128)
    alpha_2_code: str = Field(
        min_length=2, max_length=2, description="ISO alpha-2 code"
    )
    latitude: float
    longitude: float


class CountryCreateDTO(CountryBaseDTO):
    """Payload to create Country."""

    pass


class CountryUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CountryReadDTO(CountryBaseDTO):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
