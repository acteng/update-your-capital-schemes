"""Alter capital scheme table schema

Revision ID: 9d3defc17322
Revises: e14f20b7f6b2
Create Date: 2024-03-22 17:54:46.798476

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "9d3defc17322"
down_revision: Union[str, None] = "e14f20b7f6b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("CREATE SCHEMA capital_scheme")
        op.execute("ALTER TABLE capital_scheme SET SCHEMA capital_scheme")
    else:
        op.execute("ATTACH DATABASE ':memory:' AS capital_scheme")

        op.create_table(
            "capital_scheme",
            sa.Column("capital_scheme_id", sa.Integer, primary_key=True),
            sa.Column("scheme_name", sa.Text, nullable=False),
            sa.Column(
                "bid_submitting_authority_id",
                sa.Integer,
                sa.ForeignKey(
                    "authority.authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey"
                ),
            ),
            sa.Column("scheme_type_id", sa.Integer),
            sa.Column("funding_programme_id", sa.Integer),
            schema="capital_scheme",
        )
        op.execute("INSERT INTO capital_scheme.capital_scheme SELECT * FROM capital_scheme")

        with op.batch_alter_table("capital_scheme_authority_review") as batch_op:
            batch_op.drop_constraint("capital_scheme_authority_review_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_authority_review_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
                referent_schema="capital_scheme",
            )

        with op.batch_alter_table("capital_scheme_financial") as batch_op:
            batch_op.drop_constraint("capital_scheme_financial_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_financial_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
                referent_schema="capital_scheme",
            )

        with op.batch_alter_table("capital_scheme_intervention") as batch_op:
            batch_op.drop_constraint("capital_scheme_intervention_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_intervention_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
                referent_schema="capital_scheme",
            )

        with op.batch_alter_table("capital_scheme_milestone") as batch_op:
            batch_op.drop_constraint("capital_scheme_milestone_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_milestone_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
                referent_schema="capital_scheme",
            )

        op.drop_table("capital_scheme")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme.capital_scheme SET SCHEMA public")
        op.execute("DROP SCHEMA capital_scheme")
    else:
        op.create_table(
            "capital_scheme",
            sa.Column("capital_scheme_id", sa.Integer, primary_key=True),
            sa.Column("scheme_name", sa.Text, nullable=False),
            sa.Column(
                "bid_submitting_authority_id",
                sa.Integer,
                sa.ForeignKey(
                    "authority.authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey"
                ),
            ),
            sa.Column("scheme_type_id", sa.Integer),
            sa.Column("funding_programme_id", sa.Integer),
        )
        op.execute("INSERT INTO capital_scheme SELECT * FROM capital_scheme.capital_scheme")

        with op.batch_alter_table("capital_scheme_authority_review") as batch_op:
            batch_op.drop_constraint("capital_scheme_authority_review_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_authority_review_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
            )

        with op.batch_alter_table("capital_scheme_financial") as batch_op:
            batch_op.drop_constraint("capital_scheme_financial_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_financial_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
            )

        with op.batch_alter_table("capital_scheme_intervention") as batch_op:
            batch_op.drop_constraint("capital_scheme_intervention_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_intervention_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
            )

        with op.batch_alter_table("capital_scheme_milestone") as batch_op:
            batch_op.drop_constraint("capital_scheme_milestone_capital_scheme_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_milestone_capital_scheme_id_fkey",
                "capital_scheme",
                ["capital_scheme_id"],
                ["capital_scheme_id"],
            )

        op.drop_table("capital_scheme", schema="capital_scheme")

        op.execute("DETACH DATABASE capital_scheme")
