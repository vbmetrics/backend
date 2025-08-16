from typing import Optional

from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str
    # expires_in: int
    # scope: str = ""


class TokenData(SQLModel):
    email: Optional[str] = None
