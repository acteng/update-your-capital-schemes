"""Alter capital scheme type nullable

Revision ID: 911e18fe1942
Revises: 87e7afa02e44
Create Date: 2024-04-08 10:53:58.231691

"""

from typing import Sequence, Union

from alembic import op

revision: str = "911e18fe1942"
down_revision: Union[str, None] = "87e7afa02e44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("scheme_type_id", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("scheme_type_id", nullable=True)
