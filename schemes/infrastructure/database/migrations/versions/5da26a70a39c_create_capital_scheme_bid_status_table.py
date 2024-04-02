"""Create capital scheme bid status table

Revision ID: 5da26a70a39c
Revises: a58bd98c6a84
Create Date: 2024-04-02 16:30:25.914138

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "5da26a70a39c"
down_revision: Union[str, None] = "a58bd98c6a84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capital_scheme_bid_status",
        sa.Column("capital_scheme_bid_status_id", sa.Integer, primary_key=True),
        sa.Column(
            "capital_scheme_id",
            sa.Integer,
            sa.ForeignKey(
                "capital_scheme.capital_scheme.capital_scheme_id",
                name="capital_scheme_bid_status_capital_scheme_id_fkey",
            ),
            nullable=False,
        ),
        sa.Column("bid_status_id", sa.Integer, nullable=False),
        sa.Column("effective_date_from", sa.DateTime, nullable=False),
        sa.Column("effective_date_to", sa.DateTime),
        schema="capital_scheme",
    )


def downgrade() -> None:
    op.drop_table("capital_scheme_bid_status", schema="capital_scheme")
