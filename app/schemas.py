from pydantic import BaseModel
from datetime import date
from uuid import UUID

import enum

# ==== Country schema ====

class CountryBase(BaseModel):
    code: str
    name: str

class CountryCreate(CountryBase):
    pass

class Country(CountryBase):
    class Config:
        from_attributes = True

# ==== Season schema ====

class SeasonType(str, enum.Enum):
    club = "club"
    national = "national"

class SeasonBase(BaseModel):
    name: str
    season_type: SeasonType
    start_date: date
    end_date: date

class SeasonCreate(SeasonBase):
    pass

class SeasonUpdate(BaseModel):
    name: str | None = None
    season_type: SeasonType | None = None
    start_date: date | None = None
    end_date: date | None = None

class Season(SeasonBase):
    id: UUID
    class Config:
        from_attributes = True

# ==== Arena schema ====

class ArenaBase(BaseModel):
    name: str
    country_code: str
    city: str | None = None
    address: str | None = None
    capacity: int | None = None

class ArenaCreate(ArenaBase):
    pass

class ArenaUpdate(BaseModel):
    name: str | None = None
    country_code: str | None = None
    city: str | None = None
    address: str | None = None
    capacity: int | None = None

class Arena(ArenaBase):
    id: UUID

    class Config:
        from_attributes = True
