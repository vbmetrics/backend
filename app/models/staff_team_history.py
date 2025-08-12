import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .season import Season, SeasonRead
    from .staff_member import StaffMember, StaffMemberRead
    from .team import Team, TeamRead


class StaffTeamHistoryBase(SQLModel):
    role: str
    staff_member_id: UUID = Field(foreign_key="staff_member.id")
    team_id: UUID = Field(foreign_key="team.id")
    season_id: UUID = Field(foreign_key="season.id")


class StaffTeamHistory(StaffTeamHistoryBase, table=True):
    __tablename__ = "staff_team_history"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    staff_member: StaffMember = Relationship(back_populates="team_history")
    team: Team = Relationship(back_populates="staff_history")
    season: Season = Relationship(back_populates="staff_team_history")


class StaffTeamHistoryCreate(StaffTeamHistoryBase):
    pass


class StaffTeamHistoryRead(StaffTeamHistoryBase):
    id: UUID


class StaffTeamHistoryUpdate(SQLModel):
    role: Optional[str] = None


class StaffTeamHistoryReadWithDetails(StaffTeamHistoryRead):
    staff_member: Optional[StaffMemberRead] = None
    team: Optional[TeamRead] = None
    season: Optional[SeasonRead] = None
