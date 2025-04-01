"""Add authority abbreviation to authority table

Revision ID: e47d50ce7557
Revises: 41d056f8ea12
Create Date: 2025-04-01 15:49:29.200582

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e47d50ce7557"
down_revision: Union[str, None] = "41d056f8ea12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("authority", schema="authority") as batch_op:
        batch_op.add_column(sa.Column("authority_abbreviation", sa.Text))
        batch_op.create_unique_constraint("authority_authority_abbreviation_key", ["authority_abbreviation"])


def downgrade() -> None:
    with op.batch_alter_table("authority", schema="authority") as batch_op:
        batch_op.drop_column("authority_abbreviation")
