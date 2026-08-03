"""Create users table

Revision ID: bfc3cbc1bb13
Revises:
Create Date: 2023-10-20 10:15:51.912421

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "bfc3cbc1bb13"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(256), nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_table("users")
