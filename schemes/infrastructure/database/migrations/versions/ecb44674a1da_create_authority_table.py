"""Create authority table

Revision ID: ecb44674a1da
Revises: 4015380a8cf6
Create Date: 2023-10-27 12:25:56.451290

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "ecb44674a1da"
down_revision: Union[str, None] = "9bbdafd4f676"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authority",
        sa.Column("authority_id", sa.Integer, primary_key=True),
        sa.Column("authority_name", sa.Text, nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_table("authority")
