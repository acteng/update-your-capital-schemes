"""Remove capital scheme schema

Revision ID: 2b238e72b6f7
Revises: 25d12b908392
Create Date: 2026-06-16 13:51:18.797750

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "2b238e72b6f7"
down_revision: Union[str, None] = "25d12b908392"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("capital_scheme_overview", schema="capital_scheme")
    op.drop_table("capital_scheme_bid_status", schema="capital_scheme")
    op.drop_table("capital_scheme_financial", schema="capital_scheme")
    op.drop_table("capital_scheme_milestone", schema="capital_scheme")
    op.drop_table("capital_scheme_intervention", schema="capital_scheme")
    op.drop_table("capital_scheme_authority_review", schema="capital_scheme")
    op.drop_table("capital_scheme", schema="capital_scheme")

    if op.get_context().dialect.name == PGDialect.name:
        op.execute("DROP SCHEMA capital_scheme")
    else:
        op.execute("DETACH DATABASE capital_scheme")


def downgrade() -> None:
    # Not supported
    pass
