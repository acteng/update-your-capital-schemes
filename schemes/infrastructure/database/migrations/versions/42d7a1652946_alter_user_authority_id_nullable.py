"""Alter user authority id nullable

Revision ID: 42d7a1652946
Revises: 50e7242f2fc8
Create Date: 2025-04-02 11:11:58.974235

"""

from typing import Sequence, Union

from alembic import op

revision: str = "42d7a1652946"
down_revision: Union[str, None] = "50e7242f2fc8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("authority_id", nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("authority_id", nullable=False)
