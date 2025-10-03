"""ensure is_superuser with default false on user

Revision ID: d0319ba0fca1
Revises: 05ee9c692b1f
Create Date: 2025-10-03 21:00:46.468072

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d0319ba0fca1"
down_revision: Union[str, None] = "05ee9c692b1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN')
    op.execute('UPDATE "user" SET is_superuser = false WHERE is_superuser IS NULL')
    op.execute('ALTER TABLE "user" ALTER COLUMN is_superuser SET DEFAULT false')
    op.execute('ALTER TABLE "user" ALTER COLUMN is_superuser SET NOT NULL')


def downgrade() -> None:
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS is_superuser')
