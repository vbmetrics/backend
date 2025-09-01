import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .match import Match, MatchRead
    from .rally import Rally
    from .team import Team, TeamRead


class SetBase(SQLModel):
    set_number: int = Field(gt=0, description="Set number in match (1, 2, 3, etc.)")
    home_team_score: int = Field(default=0)
    away_team_score: int = Field(default=0)
    duration_minutes: Optional[int] = Field(default=None)

    # Foreign keys
    match_id: UUID = Field(foreign_key="match.id")
    winner_team_id: Optional[UUID] = Field(default=None, foreign_key="team.id")

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


class Set(SetBase, table=True):
    __tablename__ = "set"
    __table_args__ = (CheckConstraint("set_number > 0", name="positive_set_number"),)

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    match: "Match" = Relationship(back_populates="sets")
    rallies: list["Rally"] = Relationship(back_populates="set")
    winner_team: Optional["Team"] = Relationship(back_populates="won_sets")


class SetCreate(SetBase):
    pass


class SetRead(SetBase):
    id: UUID


class SetReadWithDetails(SetRead):
    match: Optional["MatchRead"] = None
    winner_team: Optional["TeamRead"] = None


class SetUpdate(SQLModel):
    home_team_score: Optional[int] = None
    away_team_score: Optional[int] = None
    winner_team_id: Optional[UUID] = None
    duration_minutes: Optional[int] = None
