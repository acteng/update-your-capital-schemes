"""Remove user authority foreign key

Revision ID: 3e6f6be8bf70
Revises: 8e77c6c5b1b8
Create Date: 2024-04-29 10:54:11.483111

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "3e6f6be8bf70"
down_revision: Union[str, None] = "8e77c6c5b1b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.drop_constraint("user_authority_id_fkey", "user")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.add_column(
            "user",
            sa.Column(
                "authority_id",
                sa.Integer,
                sa.ForeignKey("authority.authority_id", name="user_authority_id_fkey"),
                nullable=False,
            ),
        )
