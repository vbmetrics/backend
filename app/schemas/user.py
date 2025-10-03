from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    full_name: Optional[str] = Field(default=None, max_length=200)
    role: UserRole = UserRole.user
    is_active: bool = True


class UserCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=200)
    role: UserRole = UserRole.user


class UserUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(default=None, max_length=200)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    is_active: Optional[bool] = None


class UserReadDTO(UserBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
