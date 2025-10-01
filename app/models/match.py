import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .arena import Arena
    from .season import Season
    from .set import Set
    from .team import Team


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
    sets: list["Set"] = Relationship(back_populates="match")
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

    def __repr__(self) -> str:
        return f"<Match id={self.id} date={self.match_date} home={self.home_team_id} away={self.away_team_id} winner={self.winner_team_id}>"  # noqa
