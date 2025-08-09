"""Seed initial players data from csv file

Revision ID: 7557818662c0
Revises: f734b5da5dec
Create Date: 2025-08-09 15:39:27.869838

"""

import csv
import os
import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7557818662c0"
down_revision: Union[str, None] = "f734b5da5dec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    players_table = sa.table(
        "players",
        sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.column("first_name", sa.String),
        sa.column("last_name", sa.String),
        sa.column("date_of_birth", sa.Date),
        sa.column("nationality_code", sa.CHAR(2)),
        sa.column("height_cm", sa.Integer),
        sa.column("weight_kg", sa.Integer),
        sa.column("playing_position", sa.String),
        sa.column("dominant_hand", sa.String),
        sa.column("spike_reach_cm", sa.Integer),
        sa.column("block_reach_cm", sa.Integer),
        sa.column("photo_url", sa.String),
        sa.column("bio", sa.String),
    )

    csv_path = os.path.join(os.path.dirname(__file__), "../../data/players.csv")

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")

        players_data = []
        for row in reader:
            date_of_birth_str = row.get("date_of_birth", "").strip()
            if date_of_birth_str:
                date_of_birth_obj = datetime.strptime(
                    date_of_birth_str, "%d/%m/%Y"
                ).date()
            else:
                date_of_birth_obj = None

            player_entry = {
                "id": uuid.uuid4(),
                "first_name": row.get("first_name"),
                "last_name": row.get("last_name"),
                "date_of_birth": date_of_birth_obj,
                "nationality_code": row.get("nationality_code"),
                "height_cm": int(row["height_cm"]) if row.get("height_cm") else None,
                "weight_kg": int(row["weight_kg"]) if row.get("weight_kg") else None,
                "playing_position": row.get("playing_position") or None,
                "dominant_hand": row.get("dominant_hand") or None,
                "spike_reach_cm": int(row["spike_reach_cm"])
                if row.get("spike_reach_cm")
                else None,
                "block_reach_cm": int(row["block_reach_cm"])
                if row.get("block_reach_cm")
                else None,
                "photo_url": row.get("photo_url") or None,
                "bio": row.get("bio") or None,
            }

            players_data.append(player_entry)

    if players_data:
        op.bulk_insert(players_table, players_data)


def downgrade() -> None:
    op.execute("DELETE FROM players")
