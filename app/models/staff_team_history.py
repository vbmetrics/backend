import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .season import Season
    from .staff_member import StaffMember
    from .team import Team


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

    def __repr__(self) -> str:
        return f"<STH id={self.id} staff={self.staff_member_id} team={self.team_id} season={self.season_id} role={self.role}>"  # noqa
