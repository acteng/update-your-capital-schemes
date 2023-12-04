"""Create scheme intervention table

Revision ID: 128d4081b36d
Revises: 4635beaac752
Create Date: 2023-12-04 11:29:46.397798

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "128d4081b36d"
down_revision: Union[str, None] = "4635beaac752"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scheme_intervention",
        sa.Column("scheme_intervention_id", sa.Integer, primary_key=True),
        sa.Column("intervention_type_measure_id", sa.Integer, nullable=False),
        sa.Column(
            "capital_scheme_id",
            sa.Integer,
            sa.ForeignKey("capital_scheme.capital_scheme_id", name="scheme_intervention_capital_scheme_id_fkey"),
            nullable=False,
        ),
        sa.Column("intervention_value", sa.Numeric(precision=15, scale=6)),
        sa.Column("observation_type_id", sa.Integer, nullable=False),
        sa.Column("effective_date_from", sa.Date, nullable=False),
        sa.Column("effective_date_to", sa.Date),
    )


def downgrade() -> None:
    op.drop_table("scheme_intervention")
