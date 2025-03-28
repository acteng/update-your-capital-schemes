"""Add authority abbreviation to user table

Revision ID: f7845e7c8332
Revises: 8a092b49283a
Create Date: 2025-03-28 18:00:57.712589

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f7845e7c8332"
down_revision: Union[str, None] = "8a092b49283a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(
            sa.Column(
                "authority_abbreviation",
                sa.Text,
                sa.ForeignKey("authority.authority.authority_abbreviation", name="user_authority_abbreviation_fkey"),
                nullable=False,
            )
        )
        batch_op.drop_column("authority_id")


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_column("authority_abbreviation")
        batch_op.add_column(
            sa.Column(
                "authority_id",
                sa.Integer,
                sa.ForeignKey("authority.authority.authority_id", name="user_authority_id_fkey"),
                nullable=False,
            )
        )
