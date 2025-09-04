import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Column, DateTime, String, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .action import Action
    from .set import Set, SetRead
    from .team import Team, TeamRead


class RallyBase(SQLModel):
    rally_number_in_set: int = Field(gt=0, description="Rally number within the set.")
    raw_rally_code: str = Field(sa_column=Column(String(256), index=True))
    comment: Optional[str] = Field(default=None)

    # Foreign keys
    set_id: UUID = Field(foreign_key="set.id")
    serve_team_id: UUID = Field(foreign_key="team.id")
    score_team_id: UUID = Field(foreign_key="team.id")

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


class Rally(RallyBase, table=True):
    __tablename__ = "rally"
    __table_args__ = (
        UniqueConstraint("set_id", "rally_number_in_set", name="uq_set_rally_number"),
        CheckConstraint("rally_number_in_set > 0", name="ck_rally_number_positive"),
    )

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    set: "Set" = Relationship(back_populates="rallies")
    serve_team: "Team" = Relationship(
        back_populates="serve_rallies",
        sa_relationship_kwargs={"foreign_keys": "[Rally.serve_team_id]"},
    )
    score_team: "Team" = Relationship(
        back_populates="won_rallies",
        sa_relationship_kwargs={"foreign_keys": "[Rally.score_team_id]"},
    )
    actions: list["Action"] = Relationship(back_populates="rally")


class RallyCreate(RallyBase):
    pass


class RallyRead(RallyBase):
    id: UUID


class RallyReadWithDetails(RallyRead):
    set: Optional["SetRead"] = None
    serve_team: Optional["TeamRead"] = None
    score_team: Optional["TeamRead"] = None


class RallyUpdate(SQLModel):
    raw_rally_code: Optional[str] = None
    comment: Optional[str] = None
    serve_team_id: Optional[UUID] = None
    score_team_id: Optional[UUID] = None
