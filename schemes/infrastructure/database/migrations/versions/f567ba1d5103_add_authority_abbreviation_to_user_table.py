"""Add authority abbreviation to user table

Revision ID: f567ba1d5103
Revises: e47d50ce7557
Create Date: 2025-04-01 16:03:51.239121

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f567ba1d5103"
down_revision: Union[str, None] = "e47d50ce7557"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column("authority_abbreviation", sa.Text))


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_column("authority_abbreviation")
