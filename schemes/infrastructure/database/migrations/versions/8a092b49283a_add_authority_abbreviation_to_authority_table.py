"""Add authority abbreviation to authority table

Revision ID: 8a092b49283a
Revises: 41d056f8ea12
Create Date: 2025-03-28 17:37:49.042663

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "8a092b49283a"
down_revision: Union[str, None] = "41d056f8ea12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("authority", schema="authority") as batch_op:
        batch_op.add_column(sa.Column("authority_abbreviation", sa.Text, nullable=False))
        batch_op.create_unique_constraint("authority_authority_abbreviation_key", ["authority_abbreviation"])


def downgrade() -> None:
    op.drop_column("authority", "authority_abbreviation", schema="authority")
