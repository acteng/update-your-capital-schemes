"""Remove authority schema

Revision ID: c1d744bc16bd
Revises: 2b238e72b6f7
Create Date: 2026-06-16 14:08:54.833370

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "c1d744bc16bd"
down_revision: Union[str, None] = "2b238e72b6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("authority", schema="authority")

    if op.get_context().dialect.name == PGDialect.name:
        op.execute("DROP SCHEMA authority")
    else:
        op.execute("DETACH DATABASE authority")


def downgrade() -> None:
    # Not supported
    pass
