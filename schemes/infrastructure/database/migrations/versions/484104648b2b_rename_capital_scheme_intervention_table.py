"""Rename capital scheme intervention table

Revision ID: 484104648b2b
Revises: 1e1a8831755a
Create Date: 2024-03-22 11:55:17.747201

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "484104648b2b"
down_revision: Union[str, None] = "1e1a8831755a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("scheme_intervention", "capital_scheme_intervention")
    op.alter_column(
        "capital_scheme_intervention", "scheme_intervention_id", new_column_name="capital_scheme_intervention_id"
    )
    if op.get_context().dialect.name == PGDialect.name:
        op.drop_constraint("scheme_intervention_pkey", "capital_scheme_intervention")
        op.create_primary_key(
            "capital_scheme_intervention_pkey", "capital_scheme_intervention", ["capital_scheme_intervention_id"]
        )
        op.execute(
            "ALTER SEQUENCE scheme_intervention_scheme_intervention_id_seq RENAME TO capital_scheme_intervention_capital_scheme_intervention_id_seq"
        )
    with op.batch_alter_table("capital_scheme_intervention") as batch_op:
        batch_op.drop_constraint("scheme_intervention_capital_scheme_id_fkey")
        batch_op.create_foreign_key(
            "capital_scheme_intervention_capital_scheme_id_fkey",
            "capital_scheme",
            ["capital_scheme_id"],
            ["capital_scheme_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("capital_scheme_intervention") as batch_op:
        batch_op.drop_constraint("capital_scheme_intervention_capital_scheme_id_fkey")
        batch_op.create_foreign_key(
            "scheme_intervention_capital_scheme_id_fkey",
            "capital_scheme",
            ["capital_scheme_id"],
            ["capital_scheme_id"],
        )
    if op.get_context().dialect.name == PGDialect.name:
        op.execute(
            "ALTER SEQUENCE capital_scheme_intervention_capital_scheme_intervention_id_seq RENAME TO scheme_intervention_scheme_intervention_id_seq"
        )
        op.drop_constraint("capital_scheme_intervention_pkey", "capital_scheme_intervention")
        op.create_primary_key(
            "scheme_intervention_pkey", "capital_scheme_intervention", ["capital_scheme_intervention_id"]
        )
    op.alter_column(
        "capital_scheme_intervention", "capital_scheme_intervention_id", new_column_name="scheme_intervention_id"
    )
    op.rename_table("capital_scheme_intervention", "scheme_intervention")
