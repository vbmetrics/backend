import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .player import Player
    from .rally import Rally


class Action(SQLModel, table=True):
    __tablename__ = "action"
    __table_args__ = (
        UniqueConstraint("rally_id", "sequence_in_rally", name="uq_rally_sequence"),
        CheckConstraint("sequence_in_rally > 0", name="ck_action_sequence_positive"),
        CheckConstraint(
            "(start_zone BETWEEN 1 AND 9) OR start_zone IS NULL",
            name="ck_start_zone_range",
        ),
        CheckConstraint(
            "(end_zone BETWEEN 1 AND 9) OR end_zone IS NULL", name="ck_end_zone_range"
        ),
        CheckConstraint(
            "(start_subzone ~ '^[A-I]$') OR start_subzone IS NULL",
            name="ck_start_subzone_valid_char",
        ),
        CheckConstraint(
            "(end_subzone ~ '^[A-I]$') OR end_subzone IS NULL",
            name="ck_end_subzone_valid_char",
        ),
        Index("ix_action_rally_id", "rally_id"),
        Index("ix_action_player_id", "player_id"),
        Index("ix_action_rally_seq", "rally_id", "sequence_in_rally"),
    )

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    sequence_in_rally: int = Field(gt=0, description="Action number in rally.")
    raw_action_code: str = Field(sa_column=Column(String(64), index=True))

    team_context: str = Field(sa_column=Column(CHAR(1)))
    skill_code: str = Field(sa_column=Column(CHAR(1)))
    evaluation_code: str = Field(sa_column=Column(CHAR(1)))

    player_jersey_number: Optional[int] = Field(default=None)
    start_zone: Optional[int] = Field(default=None)
    end_zone: Optional[int] = Field(default=None)
    start_subzone: Optional[str] = Field(default=None, sa_column=Column(CHAR(1)))
    end_subzone: Optional[str] = Field(default=None, sa_column=Column(CHAR(1)))
    modifiers: Optional[str] = Field(default=None, sa_column=Column(String(12)))

    rally_id: UUID = Field(foreign_key="rally.id")
    player_id: Optional[UUID] = Field(default=None, foreign_key="player.id")

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

    # Relationships
    rally: "Rally" = Relationship(back_populates="actions")
    player: Optional["Player"] = Relationship(back_populates="actions")

    def __repr__(self) -> str:
        return f"<Action id={self.id} rally_id={self.rally_id} seq={self.sequence_in_rally} code={self.raw_action_code}>"  # noqa
