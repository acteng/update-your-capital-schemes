"""Alter capital scheme funding programme nullable

Revision ID: 8e77c6c5b1b8
Revises: 911e18fe1942
Create Date: 2024-04-08 15:08:19.373194

"""

from typing import Sequence, Union

from alembic import op

revision: str = "8e77c6c5b1b8"
down_revision: Union[str, None] = "911e18fe1942"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("funding_programme_id", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("funding_programme_id", nullable=True)
