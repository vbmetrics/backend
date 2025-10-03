"""add full_name column to user

Revision ID: 05ee9c692b1f
Revises: 0e5caff2780e
Create Date: 2025-10-03 20:26:57.456958

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "05ee9c692b1f"
down_revision: Union[str, None] = "0e5caff2780e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS full_name VARCHAR(200) NULL'
    )


def downgrade() -> None:
    # jeśli chcesz być restrykcyjny:
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS full_name')
