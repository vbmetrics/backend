import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .action import Action
    from .country import Country
    from .player_team_history import PlayerTeamHistory


class PlayerPosition(str, enum.Enum):
    setter = "setter"
    opposite = "opposite"
    outside_hitter = "outside_hitter"
    middle_blocker = "middle_blocker"
    libero = "libero"


class PlayerHand(str, enum.Enum):
    right = "right"
    left = "left"
    ambidextrous = "ambidextrous"


class PlayerBase(SQLModel):
    first_name: str
    last_name: str
    date_of_birth: date
    height_cm: Optional[int] = Field(default=None, gt=0)
    weight_kg: Optional[int] = Field(default=None, gt=0)
    playing_position: Optional[PlayerPosition] = Field(
        default=None, sa_column=Column(SQLAlchemyEnum(PlayerPosition))
    )
    dominant_hand: Optional[PlayerHand] = Field(
        default=None, sa_column=Column(SQLAlchemyEnum(PlayerHand))
    )
    spike_reach_cm: Optional[int] = Field(default=None, gt=0)
    block_reach_cm: Optional[int] = Field(default=None, gt=0)
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    nationality_code: str = Field(foreign_key="country.alpha_2_code")
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


class Player(PlayerBase, table=True):
    __tablename__ = "player"
    __table_args__ = (
        CheckConstraint("height_cm > 0", name="positive_height"),
        CheckConstraint("weight_kg > 0", name="positive_weight"),
        CheckConstraint("spike_reach_cm > 0", name="positive_spike_reach"),
        CheckConstraint("block_reach_cm > 0", name="positive_block_reach"),
    )

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    nationality: "Country" = Relationship(back_populates="players")
    team_histories: list["PlayerTeamHistory"] = Relationship(back_populates="player")
    actions: list["Action"] = Relationship(back_populates="player")

    def __repr__(self) -> str:
        return f"<Player id={self.id} name={self.first_name} {self.last_name} nat={self.nationality_code}>"  # noqa
