"""Alter capital scheme bid submitting authority nullable

Revision ID: 87e7afa02e44
Revises: 5da26a70a39c
Create Date: 2024-04-05 16:52:42.713837

"""

from typing import Sequence, Union

from alembic import op

revision: str = "87e7afa02e44"
down_revision: Union[str, None] = "5da26a70a39c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("bid_submitting_authority_id", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("bid_submitting_authority_id", nullable=True)
