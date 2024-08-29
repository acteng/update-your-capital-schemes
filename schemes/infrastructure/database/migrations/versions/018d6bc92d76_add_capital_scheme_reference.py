"""Add capital scheme reference

Revision ID: 018d6bc92d76
Revises: 3f8e2f1e7220
Create Date: 2024-08-29 16:30:11.805518

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "018d6bc92d76"
down_revision: Union[str, None] = "3f8e2f1e7220"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.add_column(sa.Column("scheme_reference", sa.Text))
        batch_op.create_unique_constraint("capital_scheme_scheme_reference_key", ["scheme_reference"])
    if op.get_context().dialect.name == PGDialect.name:
        op.execute(
            """
            UPDATE capital_scheme.capital_scheme
                SET scheme_reference='ATE' || LPAD(capital_scheme.capital_scheme_id::text, 5, '0')
            """
        )
    else:
        op.execute(
            """
            UPDATE capital_scheme.capital_scheme
                SET scheme_reference='ATE' || SUBSTR('00000' || capital_scheme.capital_scheme_id, -5, 5)
            """
        )
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("scheme_reference", nullable=False)


def downgrade() -> None:
    op.drop_column("capital_scheme", "scheme_reference", schema="capital_scheme")
