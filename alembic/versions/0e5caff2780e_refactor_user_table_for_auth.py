"""refactor user table for auth

Revision ID: 0e5caff2780e
Revises: 0b5e5e76b4c5
Create Date: 2025-10-03 19:48:23.789096
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "0e5caff2780e"
down_revision: Union[str, None] = "0b5e5e76b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    user_exists = bind.execute(
        sa.text("SELECT to_regclass('public.\"user\"') IS NOT NULL")
    ).scalar()
    if not user_exists:
        users_exists = bind.execute(
            sa.text("SELECT to_regclass('public.users') IS NOT NULL")
        ).scalar()
        if users_exists:
            op.rename_table("users", "user")
        else:
            raise RuntimeError(
                'Neither table "users" nor "user" exists — cannot proceed.'
            )

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
            CREATE TYPE userrole AS ENUM ('admin','coach','analyst','user');
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='user' AND column_name='role'
        ) THEN
            ALTER TABLE "user" ADD COLUMN role TEXT;
        END IF;
    END$$;
    """)

    op.execute('UPDATE "user" SET role = LOWER(role) WHERE role IS NOT NULL;')
    op.execute("UPDATE \"user\" SET role = 'user' WHERE role IS NULL;")

    op.execute('ALTER TABLE "user" ALTER COLUMN role DROP DEFAULT;')
    op.execute(
        'ALTER TABLE "user" ALTER COLUMN role TYPE userrole USING role::userrole;'
    )
    op.execute("ALTER TABLE \"user\" ALTER COLUMN role SET DEFAULT 'user';")
    op.execute('ALTER TABLE "user" ALTER COLUMN role SET NOT NULL;')


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_user_email;")
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'user' AND c.conname = 'uq_user_email'
        ) THEN
            ALTER TABLE "user" DROP CONSTRAINT uq_user_email;
        END IF;
    END$$;
    """)

    op.execute('ALTER TABLE "user" ALTER COLUMN role DROP DEFAULT;')
    op.execute('ALTER TABLE "user" ALTER COLUMN role TYPE TEXT;')
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
            DROP TYPE userrole;
        END IF;
    END$$;
    """)
