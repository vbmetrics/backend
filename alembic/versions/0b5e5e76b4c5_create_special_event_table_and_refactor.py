"""create special_event table and refactor

Revision ID: 0b5e5e76b4c5
Revises: b34613bcbb4f
Create Date: 2025-10-03 15:21:26.805637

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b5e5e76b4c5"
down_revision: Union[str, None] = "b34613bcbb4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "special_event",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "event_type",
            sa.Enum(
                "timeout",
                "substitution",
                "card",
                "challenge",
                "other",
                name="specialeventtype",
            ),
            nullable=False,
        ),
        sa.Column("raw_special_code", sa.String(length=128), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("set_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "details", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),  # JSONB for Postgres
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["match_id"], ["match.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["set_id"], ["set.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["player_id"], ["player.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_special_event_raw_code", "special_event", ["raw_special_code"])


def downgrade() -> None:
    op.drop_index("ix_special_event_raw_code", table_name="special_event")
    op.drop_table("special_event")
