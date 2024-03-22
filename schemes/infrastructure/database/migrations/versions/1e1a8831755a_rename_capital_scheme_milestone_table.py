"""Rename capital scheme milestone table

Revision ID: 1e1a8831755a
Revises: 0557bce51693
Create Date: 2024-03-22 11:52:10.575564

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "1e1a8831755a"
down_revision: Union[str, None] = "0557bce51693"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("scheme_milestone", "capital_scheme_milestone")
    op.alter_column("capital_scheme_milestone", "scheme_milestone_id", new_column_name="capital_scheme_milestone_id")
    if op.get_context().dialect.name == PGDialect.name:
        op.drop_constraint("scheme_milestone_pkey", "capital_scheme_milestone")
        op.create_primary_key(
            "capital_scheme_milestone_pkey", "capital_scheme_milestone", ["capital_scheme_milestone_id"]
        )
        op.execute(
            "ALTER SEQUENCE scheme_milestone_scheme_milestone_id_seq RENAME TO capital_scheme_milestone_capital_scheme_milestone_id_seq"
        )
    with op.batch_alter_table("capital_scheme_milestone") as batch_op:
        batch_op.drop_constraint("scheme_milestone_capital_scheme_id_fkey")
        batch_op.create_foreign_key(
            "capital_scheme_milestone_capital_scheme_id_fkey",
            "capital_scheme",
            ["capital_scheme_id"],
            ["capital_scheme_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("capital_scheme_milestone") as batch_op:
        batch_op.drop_constraint("capital_scheme_milestone_capital_scheme_id_fkey")
        batch_op.create_foreign_key(
            "scheme_milestone_capital_scheme_id_fkey",
            "capital_scheme",
            ["capital_scheme_id"],
            ["capital_scheme_id"],
        )
    if op.get_context().dialect.name == PGDialect.name:
        op.execute(
            "ALTER SEQUENCE capital_scheme_milestone_capital_scheme_milestone_id_seq RENAME TO scheme_milestone_scheme_milestone_id_seq"
        )
        op.drop_constraint("capital_scheme_milestone_pkey", "capital_scheme_milestone")
        op.create_primary_key("scheme_milestone_pkey", "capital_scheme_milestone", ["capital_scheme_milestone_id"])
    op.alter_column("capital_scheme_milestone", "capital_scheme_milestone_id", new_column_name="scheme_milestone_id")
    op.rename_table("capital_scheme_milestone", "scheme_milestone")
