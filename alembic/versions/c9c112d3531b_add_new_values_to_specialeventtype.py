"""add new values to specialeventtype

Revision ID: c9c112d3531b
Revises: aabc82f9c83a
Create Date: 2026-02-24 22:34:31.972237

"""
from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c9c112d3531b'
down_revision: Union[str, None] = 'aabc82f9c83a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Wymuszenie dodania słów do Enuma w PostgreSQL
    op.execute("ALTER TYPE specialeventtype ADD VALUE IF NOT EXISTS 'fault'")
    op.execute("ALTER TYPE specialeventtype ADD VALUE IF NOT EXISTS 'challenge'")
    op.execute("ALTER TYPE specialeventtype ADD VALUE IF NOT EXISTS 'other'")


def downgrade() -> None:
    pass
