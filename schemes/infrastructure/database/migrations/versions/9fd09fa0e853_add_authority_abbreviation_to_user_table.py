"""Add authority abbreviation to user table

Revision ID: 9fd09fa0e853
Revises: 64a978a937f4
Create Date: 2024-04-09 14:56:36.467102

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9fd09fa0e853"
down_revision: Union[str, None] = "64a978a937f4"
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
