"""Create scheme milestone table

Revision ID: adf85fb23025
Revises: f0073277add0
Create Date: 2023-11-15 10:06:25.592501

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "adf85fb23025"
down_revision: Union[str, None] = "f0073277add0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scheme_milestone",
        sa.Column("scheme_milestone_id", sa.Integer, primary_key=True),
        sa.Column(
            "capital_scheme_id",
            sa.Integer,
            sa.ForeignKey("capital_scheme.capital_scheme_id", name="scheme_milestone_capital_scheme_id_fkey"),
            nullable=False,
        ),
        sa.Column("milestone_id", sa.Integer, nullable=False),
        sa.Column("status_date", sa.Date, nullable=False),
        sa.Column("observation_type_id", sa.Integer, nullable=False),
        sa.Column("effective_date_from", sa.Date, nullable=False),
        sa.Column("effective_date_to", sa.Date),
    )


def downgrade() -> None:
    op.drop_table("scheme_milestone")
