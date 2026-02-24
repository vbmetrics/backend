import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .set import Set
    from .team import Team


class LineupBase(SQLModel):
    # Relacje nadrzędne
    set_id: UUID = Field(foreign_key="set.id")
    team_id: UUID = Field(foreign_key="team.id")

    # Wyjściowa szóstka
    p1_id: UUID = Field(foreign_key="player.id")
    p2_id: UUID = Field(foreign_key="player.id")
    p3_id: UUID = Field(foreign_key="player.id")
    p4_id: UUID = Field(foreign_key="player.id")
    p5_id: UUID = Field(foreign_key="player.id")
    p6_id: UUID = Field(foreign_key="player.id")

    # Libero (opcjonalny w amatorskich ligach)
    libero_id: Optional[UUID] = Field(default=None, foreign_key="player.id")

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


class Lineup(LineupBase, table=True):
    __tablename__ = "lineup"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relacje
    team: "Team" = Relationship()
    set: Optional["Set"] = Relationship(back_populates="lineups")

    def __repr__(self) -> str:
        return f"<Lineup set={self.set_id} team={self.team_id}>"
