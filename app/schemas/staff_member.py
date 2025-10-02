from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.staff_member import StaffRoleType


class StaffMemberBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role_type: StaffRoleType
    nationality_code: str = Field(min_length=2, max_length=2)


class StaffMemberCreateDTO(StaffMemberBaseDTO):
    """Payload to create StaffMember."""


class StaffMemberUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    role_type: Optional[StaffRoleType] = None
    nationality_code: Optional[str] = Field(default=None, min_length=2, max_length=2)


class StaffMemberReadDTO(StaffMemberBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
