import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .lineup import Lineup
    from .match import Match
    from .rally import Rally
    from .set_state import SetState
    from .special_event import SpecialEvent
    from .team import Team


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
    rallies: list["Rally"] = Relationship(
        back_populates="set",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"} # DODANE
    )
    set_state: Optional["SetState"] = Relationship(
        back_populates="set",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"} # DODANE
    )
    special_events: list["SpecialEvent"] = Relationship(
        back_populates="set",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    lineups: list["Lineup"] = Relationship(
        back_populates="set",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    winner_team: Optional["Team"] = Relationship(back_populates="won_sets")

    def __repr__(self) -> str:
        return f"<Set id={self.id} match={self.match_id} no={self.set_number} {self.home_team_score}:{self.away_team_score} winner={self.winner_team_id}>"  # noqa
