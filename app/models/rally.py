import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Column, DateTime, String, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .action import Action
    from .set import Set
    from .team import Team


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

    def __repr__(self) -> str:
        return f"<Rally id={self.id} set={self.set_id} no={self.rally_number_in_set}>"
