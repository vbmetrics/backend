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
    from .player import Player, PlayerRead
    from .rally import Rally, RallyRead


class ActionBase(SQLModel):
    sequence_in_rally: int = Field(gt=0, description="Action number in rally.")
    raw_action_code: str = Field(sa_column=Column(String(64), index=True))

    # Parsed values
    team_context: str = Field(sa_column=Column(CHAR(1)))  # description
    skill_code: str = Field(sa_column=Column(CHAR(1)))  # description
    evaluation_code: str = Field(sa_column=Column(CHAR(1)))  # description

    # Optional data
    player_jersey_number: Optional[int] = Field(default=None)
    start_zone: Optional[int] = Field(default=None)
    end_zone: Optional[int] = Field(default=None)
    start_subzone: Optional[str] = Field(default=None, sa_column=Column(CHAR(1)))
    end_subzone: Optional[str] = Field(default=None, sa_column=Column(CHAR(1)))
    modifiers: Optional[str] = Field(default=None, max_length=12)  # max_length

    # Foreign keys
    rally_id: UUID = Field(foreign_key="rally.id")
    player_id: Optional[UUID] = Field(default=None, foreign_key="player.id")

    # Timestamps
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


class Action(ActionBase, table=True):
    __tablename__ = "action"
    __table_args__ = (
        UniqueConstraint("rally_id", "sequence_in_rally", name="uq_rally_sequence"),
        Index("ix_action_rally_seq_desc", "rally_id", "sequence_in_rally"),
        CheckConstraint("sequence_in_rally > 0", name="ck_action_sequence_positive"),
        CheckConstraint(
            "start_zone >= 1 AND start_zone <= 9", name="ck_start_zone_range"
        ),
        CheckConstraint("end_zone >= 1 AND end_zone <= 9", name="ck_end_zone_range"),
        CheckConstraint(
            "(start_subzone IN ('A','B','C','D','E','F','G','H','I')) OR start_subzone IS NULL",  # noqa: E501
            name="ck_start_subzone_in",
        ),
        CheckConstraint(
            "(end_subzone IN ('A','B','C','D','E','F','G','H','I')) OR end_subzone IS NULL",  # noqa: E501
            name="ck_end_subzone_in",
        ),
    )

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    rally: "Rally" = Relationship(back_populates="actions")
    player: Optional["Player"] = Relationship(back_populates="actions")


class ActionCreate(ActionBase):
    pass


class ActionRead(ActionBase):
    id: UUID


class ActionReadWithDetails(ActionRead):
    rally: Optional["RallyRead"] = None
    player: Optional["PlayerRead"] = None


class ActionUpdate(SQLModel):
    raw_action_code: Optional[str] = None
    team_context: Optional[str] = None
    skill_code: Optional[str] = None
    evaluation_code: Optional[str] = None
    start_zone: Optional[int] = None
    end_zone: Optional[int] = None
    start_subzone: Optional[str] = None
    end_subzone: Optional[str] = None
    modifiers: Optional[str] = None
    player_jersey_number: Optional[int] = None
    player_id: Optional[UUID] = None
