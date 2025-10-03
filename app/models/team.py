import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .arena import Arena
    from .country import Country
    from .match import Match
    from .player_team_history import PlayerTeamHistory
    from .rally import Rally
    from .set import Set
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
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )


class Team(TeamBase, table=True):
    __tablename__ = "team"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    country: "Country" = Relationship(back_populates="teams")
    home_arena: Optional["Arena"] = Relationship(back_populates="home_team")
    staff_histories: list["StaffTeamHistory"] = Relationship(back_populates="team")
    player_histories: list["PlayerTeamHistory"] = Relationship(back_populates="team")
    won_sets: list["Set"] = Relationship(back_populates="winner_team")
    home_matches: list["Match"] = Relationship(
        back_populates="home_team",
        sa_relationship_kwargs={"foreign_keys": "[Match.home_team_id]"},
    )
    away_matches: list["Match"] = Relationship(
        back_populates="away_team",
        sa_relationship_kwargs={"foreign_keys": "[Match.away_team_id]"},
    )
    serve_rallies: list["Rally"] = Relationship(
        back_populates="serve_team",
        sa_relationship_kwargs={"foreign_keys": "[Rally.serve_team_id]"},
    )
    won_rallies: list["Rally"] = Relationship(
        back_populates="score_team",
        sa_relationship_kwargs={"foreign_keys": "[Rally.score_team_id]"},
    )

    def __repr__(self) -> str:
        return f"<Team id={self.id} name={self.name} type={self.team_type} country={self.country_code}>"  # noqa
