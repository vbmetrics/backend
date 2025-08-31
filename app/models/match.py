import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .arena import Arena, ArenaRead
    from .season import Season, SeasonRead
    from .team import Team, TeamRead


class MatchBase(SQLModel):
    match_date: Optional[date] = Field(default=None)
    spectators: Optional[int] = Field(default=None)
    home_team_score: Optional[int] = Field(default=None)
    away_team_score: Optional[int] = Field(default=None)

    # Foreign keys
    season_id: UUID = Field(foreign_key="season.id")
    home_team_id: UUID = Field(foreign_key="team.id")
    away_team_id: UUID = Field(foreign_key="team.id")
    winner_team_id: Optional[UUID] = Field(default=None, foreign_key="team.id")
    arena_id: Optional[UUID] = Field(default=None, foreign_key="arena.id")

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


class Match(MatchBase, table=True):
    __tablename__ = "match"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    season: Optional["Season"] = Relationship(back_populates="matches")
    arena: Optional["Arena"] = Relationship(back_populates="matches")
    home_team: "Team" = Relationship(
        back_populates="home_matches",
        sa_relationship_kwargs={"foreign_keys": "[Match.home_team_id]"},
    )
    away_team: "Team" = Relationship(
        back_populates="away_matches",
        sa_relationship_kwargs={"foreign_keys": "[Match.away_team_id]"},
    )
    winner_team: Optional["Team"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.winner_team_id]"}
    )


class MatchCreate(MatchBase):
    pass


class MatchRead(MatchBase):
    id: UUID


class MatchReadWithDetails(MatchRead):
    season: Optional["SeasonRead"] = None
    arena: Optional["ArenaRead"] = None
    home_team: Optional["TeamRead"] = None
    away_team: Optional["TeamRead"] = None
    winner_team: Optional["TeamRead"] = None


class MatchUpdate(SQLModel):
    match_date: Optional[date] = None
    arena_id: Optional[UUID] = None
    spectators: Optional[int] = None
    home_team_score: Optional[int] = None
    away_team_score: Optional[int] = None
    winner_team_id: Optional[UUID] = None
