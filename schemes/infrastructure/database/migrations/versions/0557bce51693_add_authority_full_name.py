"""Add authority full name

Revision ID: 0557bce51693
Revises: bfb7ab78f323
Create Date: 2024-03-22 11:48:59.400863

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0557bce51693"
down_revision: str | None = "bfb7ab78f323"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("authority", sa.Column("authority_full_name", sa.Text))
    op.execute("UPDATE authority SET authority_full_name=authority_name")
    with op.batch_alter_table("authority") as batch_op:
        batch_op.alter_column("authority_full_name", nullable=False)
        batch_op.drop_column("authority_name")


def downgrade() -> None:
    op.add_column("authority", sa.Column("authority_name", sa.Text, unique=True))
    op.execute("UPDATE authority SET authority_name=authority_full_name")
    with op.batch_alter_table("authority") as batch_op:
        batch_op.alter_column("authority_name", nullable=False)
        batch_op.drop_column("authority_full_name")
