"""Alter user authority id nullable

Revision ID: 42d7a1652946
Revises: 50e7242f2fc8
Create Date: 2025-04-02 11:11:58.974235

"""

from collections.abc import Sequence

from alembic import op

revision: str = "42d7a1652946"
down_revision: str | None = "50e7242f2fc8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("authority_id", nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("authority_id", nullable=False)
