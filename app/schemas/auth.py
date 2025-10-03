from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenPairDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshDTO(BaseModel):
    refresh_token: str


class MeReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
