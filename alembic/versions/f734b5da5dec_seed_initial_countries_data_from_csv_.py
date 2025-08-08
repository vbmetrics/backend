"""Seed initial countries data from csv file

Revision ID: f734b5da5dec
Revises: cf39002529e7
Create Date: 2025-08-08 16:08:11.123531

"""

import csv
import os
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f734b5da5dec"
down_revision: Union[str, None] = "cf39002529e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    csv_path = os.path.join(
        os.path.dirname(__file__), "../../data/countries.csv"
    )  # TODO: Path library?

    with open(csv_path) as f:
        reader = csv.DictReader(f)

        countries_data = [
            {
                "alpha_2_code": row["alpha_2_code"],
                "name": row["name"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            }
            for row in reader
        ]

    if countries_data:
        country_table = sa.table(
            "countries",
            sa.column("alpha_2_code", sa.CHAR(length=2)),
            sa.column("name", sa.String),
            sa.column("latitude", sa.Float),
            sa.column("longitude", sa.Float),
        )

        op.bulk_insert(country_table, countries_data)


def downgrade() -> None:
    # It may be more precise, but it's initial data, so all can be deleted as well
    op.execute("DELETE FROM countries")
