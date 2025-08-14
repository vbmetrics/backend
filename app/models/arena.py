import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .country import Country, CountryRead
    from .team import Team


class ArenaBase(SQLModel):
    name: str
    city: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = Field(default=None, gt=0)
    country_code: str = Field(foreign_key="country.alpha_2_code")


class Arena(ArenaBase, table=True):
    __tablename__ = "arena"
    __table_args__ = (CheckConstraint("capacity > 0", name="positive_capacity"),)

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    country: "Country" = Relationship(back_populates="arenas")
    home_team: list["Team"] = Relationship(back_populates="home_arena")


class ArenaCreate(ArenaBase):
    pass


class ArenaRead(ArenaBase):
    id: UUID


class ArenaReadWithCountry(ArenaRead):
    country: Optional["CountryRead"] = None


class ArenaUpdate(SQLModel):
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    country_code: Optional[str] = None
