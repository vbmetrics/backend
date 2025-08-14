import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .player import Player, PlayerRead
    from .season import Season, SeasonRead
    from .team import Team, TeamRead


class PlayerTeamHistoryBase(SQLModel):
    start_date: date
    end_date: Optional[date] = None
    jersey_number: Optional[int] = Field(default=None, gt=0)

    # Foreign keys
    player_id: UUID = Field(foreign_key="player.id")
    team_id: UUID = Field(foreign_key="team.id")
    season_id: UUID = Field(foreign_key="season.id")


class PlayerTeamHistory(PlayerTeamHistoryBase, table=True):
    __tablename__ = "player_team_history"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    player: "Player" = Relationship(back_populates="team_histories")
    team: "Team" = Relationship(back_populates="player_histories")
    season: "Season" = Relationship(back_populates="player_team_histories")


class PlayerTeamHistoryCreate(PlayerTeamHistoryBase):
    pass


class PlayerTeamHistoryRead(PlayerTeamHistoryBase):
    id: UUID


class PlayerTeamHistoryUpdate(SQLModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    jersey_number: Optional[int] = None


class PlayerTeamHistoryReadWithDetails(PlayerTeamHistoryRead):
    player: Optional["PlayerRead"] = None
    team: Optional["TeamRead"] = None
    season: Optional["SeasonRead"] = None
