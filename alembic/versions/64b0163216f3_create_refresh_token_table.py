"""create refresh_token table

Revision ID: 64b0163216f3
Revises: d0319ba0fca1
Create Date: 2025-10-03 21:46:47.410238

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "64b0163216f3"
down_revision: Union[str, None] = "d0319ba0fca1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    exists = bind.execute(
        sa.text("SELECT to_regclass('public.refresh_token') IS NOT NULL")
    ).scalar()

    if not exists:
        op.create_table(
            "refresh_token",
            sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column(
                "jti", sa.String(length=36), nullable=False, unique=True, index=True
            ),
            sa.Column(
                "user_id",
                psql.UUID(as_uuid=True),
                sa.ForeignKey("user.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("user_agent", sa.String(length=512), nullable=True),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
        # pomocnicze indeksy pod częste zapytania
        op.create_index(
            "ix_refresh_token_user_id_revoked",
            "refresh_token",
            ["user_id", "revoked_at"],
        )
        op.create_index("ix_refresh_token_expires_at", "refresh_token", ["expires_at"])


def downgrade() -> None:
    op.drop_table("refresh_token")
