from typing import TYPE_CHECKING, Optional

from sqlalchemy import CHAR
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .arena import Arena
    from .player import Player
    from .staff_member import StaffMember
    from .team import Team


class CountryBase(SQLModel):
    name: str = Field(unique=True)
    alpha_2_code: str = Field(sa_column=Column(CHAR(2), primary_key=True))
    latitude: float
    longitude: float


class Country(CountryBase, table=True):
    __tablename__ = "country"

    # Relationships
    arenas: list["Arena"] = Relationship(back_populates="country")
    staff_members: list["StaffMember"] = Relationship(back_populates="nationality")
    players: list["Player"] = Relationship(back_populates="nationality")
    teams: list["Team"] = Relationship(back_populates="country")


class CountryCreate(CountryBase):
    pass


class CountryRead(CountryBase):
    pass


class CountryUpdate(SQLModel):
    name: Optional[str] = None
