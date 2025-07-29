from pydantic import BaseModel
from datetime import date
from uuid import UUID

import enum

class SeasonType(str, enum.Enum):
    club = "club"
    national = "national"

class CountryBase(BaseModel):
    code: str
    name: str

class CountryCreate(CountryBase):
    pass

class Country(CountryBase):
    class Config:
        from_attributes = True

class SeasonBase(BaseModel):
    name: str
    season_type: SeasonType
    start_date: date
    end_date: date

class SeasonCreate(SeasonBase):
    pass

class Season(SeasonBase):
    id: UUID
    class Config:
        from_attributes = True
