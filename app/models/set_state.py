import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from .set import Set
from .team import Team


class SetStateBase(SQLModel):
    # Kto serwuje w następnym rally (stan "po poprzednim punkcie")
    serving_team_id: UUID = Field(foreign_key="team.id")
    serving_index: int = Field(default=0, ge=0, le=5)

    # Rotacje po 6 zawodników (UUID graczy) – kolejność zgodna z P1..P6
    rotation_home: list[str] = Field(
        sa_column=Column(JSONB, nullable=False, server_default="[]")
    )
    rotation_away: list[str] = Field(
        sa_column=Column(JSONB, nullable=False, server_default="[]")
    )

    # Libero (opcjonalnie)
    libero_home_id: Optional[UUID] = None
    libero_away_id: Optional[UUID] = None

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


class SetState(SetStateBase, table=True):
    __tablename__ = "set_state"
    __table_args__ = (UniqueConstraint("set_id", name="uq_set_state_set_id"),)

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    set_id: UUID = Field(foreign_key="set.id", nullable=False, index=True, unique=True)

    # Relacje
    set: Set = Relationship()
    serving_team: Team = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[SetState.serving_team_id]"}
    )

    def __repr__(self) -> str:
        return f"<SetState set={self.set_id} serving_team={self.serving_team_id} idx={self.serving_index}>"  # noqa
