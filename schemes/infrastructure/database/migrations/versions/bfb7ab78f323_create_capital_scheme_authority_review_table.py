"""Create capital scheme authority review table

Revision ID: bfb7ab78f323
Revises: e7053d7f92d2
Create Date: 2024-02-20 11:05:06.222274

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "bfb7ab78f323"
down_revision: Union[str, None] = "e7053d7f92d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capital_scheme_authority_review",
        sa.Column("capital_scheme_authority_review_id", sa.Integer, primary_key=True),
        sa.Column(
            "capital_scheme_id",
            sa.Integer,
            sa.ForeignKey(
                "capital_scheme.capital_scheme_id", name="capital_scheme_authority_review_capital_scheme_id_fkey"
            ),
            nullable=False,
        ),
        sa.Column("review_date", sa.DateTime, nullable=False),
        sa.Column("data_source_id", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("capital_scheme_authority_review")
