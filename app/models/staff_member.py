import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .country import Country
    from .staff_team_history import StaffTeamHistory


class StaffRoleType(str, enum.Enum):
    head_coach = "head_coach"
    assistant = "assistant"


class StaffMemberBase(SQLModel):
    first_name: str
    last_name: str
    role_type: StaffRoleType = Field(sa_column=Column(SQLAlchemyEnum(StaffRoleType)))
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


class StaffMember(StaffMemberBase, table=True):
    __tablename__ = "staff_member"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    nationality: "Country" = Relationship(back_populates="staff_members")
    team_histories: list["StaffTeamHistory"] = Relationship(
        back_populates="staff_member"
    )

    def __repr__(self) -> str:
        return f"<StaffMember id={self.id} name={self.first_name} {self.last_name} role={self.role_type}>"  # noqa
