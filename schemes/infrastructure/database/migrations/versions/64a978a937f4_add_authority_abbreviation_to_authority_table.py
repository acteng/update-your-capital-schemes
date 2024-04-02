"""Add authority abbreviation to authority table

Revision ID: 64a978a937f4
Revises: 8e77c6c5b1b8
Create Date: 2024-04-09 14:50:26.222284

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "64a978a937f4"
down_revision: Union[str, None] = "8e77c6c5b1b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("authority", schema="authority") as batch_op:
        batch_op.add_column(sa.Column("authority_abbreviation", sa.Text, nullable=False))
        batch_op.create_unique_constraint("authority_authority_abbreviation_key", ["authority_abbreviation"])


def downgrade() -> None:
    with op.batch_alter_table("authority", schema="authority") as batch_op:
        batch_op.drop_column("authority_abbreviation")
