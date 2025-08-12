import enum
import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Column, Field, Relationship, SQLModel

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


class StaffMember(StaffMemberBase, table=True):
    __tablename__ = "staff_member"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    nationality: Country = Relationship(back_populates="staff_member")
    team_history: list[StaffTeamHistory] = Relationship(back_populates="staff_member")


class StaffMemberCreate(StaffMemberBase):
    pass


class StaffMemberRead(StaffMemberBase):
    id: UUID


class StaffMemberUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_type: Optional[StaffRoleType] = None
    nationality_code: Optional[str] = None
