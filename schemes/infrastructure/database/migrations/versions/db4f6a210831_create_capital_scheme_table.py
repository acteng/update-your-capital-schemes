"""Create capital scheme table

Revision ID: db4f6a210831
Revises: b0244825d57f
Create Date: 2023-11-02 10:53:07.714038

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "db4f6a210831"
down_revision: Union[str, None] = "b0244825d57f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capital_scheme",
        sa.Column("capital_scheme_id", sa.Integer(), primary_key=True),
        sa.Column("scheme_name", sa.Text(), nullable=False),
        sa.Column(
            "bid_submitting_authority_id",
            sa.Integer(),
            sa.ForeignKey("authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey"),
        ),
    )


def downgrade() -> None:
    op.drop_table("capital_scheme")
