"""Alter user authority abbreviation nullable

Revision ID: 50e7242f2fc8
Revises: f567ba1d5103
Create Date: 2025-04-01 17:42:56.812595

"""

from typing import Sequence, Union

from alembic import op

revision: str = "50e7242f2fc8"
down_revision: Union[str, None] = "f567ba1d5103"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("authority_abbreviation", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("authority_abbreviation", nullable=True)
