from pydantic import BaseModel
from datetime import date
import uuid

class TeamBase(BaseModel):
    base_name: str

class Match(BaseModel):
    id: uuid.UUID
    date: date
    score: str | None = None
    status: str | None = None
    home_team: TeamBase
    away_team: TeamBase

    class Config:
        from_attributes = True # formerly orm_mode = True
