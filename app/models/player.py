import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import CheckConstraint, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
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
    nationality: Country = Relationship(back_populates="player")
    team_history: list["PlayerTeamHistory"] = Relationship(back_populates="player")


class PlayerCreate(PlayerBase):
    pass


class PlayerRead(PlayerBase):
    id: UUID


class PlayerUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    playing_position: Optional[PlayerPosition] = None
    dominant_hand: Optional[PlayerHand] = None
    spike_reach_cm: Optional[int] = None
    block_reach_cm: Optional[int] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    nationality_code: Optional[str] = None
