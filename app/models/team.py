import enum
import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .arena import Arena
    from .country import Country
    from .player_team_history import PlayerTeamHistory
    from .staff_team_history import StaffTeamHistory


class TeamType(str, enum.Enum):
    club = "club"
    national = "national"


class TeamBase(SQLModel):
    name: str = Field(unique=True)
    team_type: TeamType = Field(sa_column=Column("team_type", SQLAlchemyEnum(TeamType)))
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    country_code: str = Field(foreign_key="country.alpha_2_code")
    home_arena_id: Optional[UUID] = Field(default=None, foreign_key="arena.id")


class Team(TeamBase, table=True):
    __tablename__ = "team"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    country: Country = Relationship(back_populates="team")
    home_arena: Optional[Arena] = Relationship(back_populates="home_team")
    staff_history: list[StaffTeamHistory] = Relationship(back_populates="team")
    player_history: list[PlayerTeamHistory] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: UUID


class TeamUpdate(SQLModel):
    name: Optional[str] = None
    team_type: Optional[TeamType] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    country_code: Optional[str] = None
    home_arena_id: Optional[UUID] = None
