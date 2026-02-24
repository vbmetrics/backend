import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import (
    Column,
    DateTime,
    String,
    func,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB as JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .match import Match
    from .player import Player
    from .set import Set
    from .team import Team


class SpecialEventType(str, enum.Enum):
    timeout = "timeout"
    substitution = "substitution"
    card = "card"
    challenge = "challenge"
    fault = "fault"
    other = "other"


class SpecialEventBase(SQLModel):
    event_type: SpecialEventType = Field(
        sa_column=Column(SQLAlchemyEnum(SpecialEventType))
    )
    raw_special_code: str = Field(sa_column=Column(String(128), index=True))

    match_id: UUID = Field(foreign_key="match.id")
    set_id: Optional[UUID] = Field(default=None, foreign_key="set.id")
    team_id: Optional[UUID] = Field(default=None, foreign_key="team.id")
    player_id: Optional[UUID] = Field(default=None, foreign_key="player.id")

    occurred_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    details: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )

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


class SpecialEvent(SpecialEventBase, table=True):
    __tablename__ = "special_event"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    match: "Match" = Relationship(back_populates="special_events")
    set: Optional["Set"] = Relationship(back_populates="special_events")
    team: Optional["Team"] = Relationship(back_populates="special_events")
    player: Optional["Player"] = Relationship(back_populates="special_events")

    def __repr__(self) -> str:
        return f"<SpecialEvent id={self.id} type={self.event_type} match={self.match_id} set={self.set_id}>"  # noqa
