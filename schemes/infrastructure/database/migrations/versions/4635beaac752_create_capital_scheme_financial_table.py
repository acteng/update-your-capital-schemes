"""Create capital scheme financial table

Revision ID: 4635beaac752
Revises: adf85fb23025
Create Date: 2023-11-20 11:20:54.943880

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "4635beaac752"
down_revision: Union[str, None] = "adf85fb23025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capital_scheme_financial",
        sa.Column("capital_scheme_financial_id", sa.Integer, primary_key=True),
        sa.Column(
            "capital_scheme_id",
            sa.Integer,
            sa.ForeignKey("capital_scheme.capital_scheme_id", name="capital_scheme_financial_capital_scheme_id_fkey"),
            nullable=False,
        ),
        sa.Column("financial_type_id", sa.Integer, nullable=False),
        sa.Column("amount", sa.Numeric, nullable=False),
        sa.Column("effective_date_from", sa.Date, nullable=False),
        sa.Column("effective_date_to", sa.Date),
        sa.Column("data_source_id", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("capital_scheme_financial")
