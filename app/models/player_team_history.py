import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .player import Player
    from .season import Season
    from .team import Team


class PlayerTeamHistoryBase(SQLModel):
    start_date: date
    end_date: Optional[date] = None
    jersey_number: Optional[int] = Field(default=None, gt=0)

    # Foreign keys
    player_id: UUID = Field(foreign_key="player.id")
    team_id: UUID = Field(foreign_key="team.id")
    season_id: UUID = Field(foreign_key="season.id")

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


class PlayerTeamHistory(PlayerTeamHistoryBase, table=True):
    __tablename__ = "player_team_history"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    player: "Player" = Relationship(back_populates="team_histories")
    team: "Team" = Relationship(back_populates="player_histories")
    season: "Season" = Relationship(back_populates="player_team_histories")

    def __repr__(self) -> str:
        return f"<PTH id={self.id} player={self.player_id} team={self.team_id} season={self.season_id} {self.start_date}->{self.end_date}>"  # noqa
