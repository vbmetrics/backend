import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
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


class StaffTeamHistory(StaffTeamHistoryBase, table=True):
    __tablename__ = "staff_team_history"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    staff_member: "StaffMember" = Relationship(back_populates="team_histories")
    team: "Team" = Relationship(back_populates="staff_histories")
    season: "Season" = Relationship(back_populates="staff_team_histories")


class StaffTeamHistoryCreate(StaffTeamHistoryBase):
    pass


class StaffTeamHistoryRead(StaffTeamHistoryBase):
    id: UUID


class StaffTeamHistoryUpdate(SQLModel):
    role: Optional[str] = None


class StaffTeamHistoryReadWithDetails(StaffTeamHistoryRead):
    staff_member: Optional["StaffMemberRead"] = None
    team: Optional["TeamRead"] = None
    season: Optional["SeasonRead"] = None
