import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .player_team_history import PlayerTeamHistory
    from .staff_team_history import StaffTeamHistory


class SeasonType(str, enum.Enum):
    club = "club"
    national = "national"


class SeasonBase(SQLModel):
    name: str = Field(unique=True)
    season_type: SeasonType = Field(
        sa_column=Column("type", SQLAlchemyEnum(SeasonType))
    )
    start_date: date
    end_date: date


class Season(SeasonBase, table=True):
    __tablename__ = "season"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    staff_team_history: list[StaffTeamHistory] = Relationship(back_populates="season")
    player_team_history: list[PlayerTeamHistory] = Relationship(back_populates="season")


class SeasonCreate(SeasonBase):
    pass


class SeasonRead(SeasonBase):
    id: UUID


class SeasonUpdate(SQLModel):
    name: Optional[str] = None
    season_type: Optional[SeasonType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
