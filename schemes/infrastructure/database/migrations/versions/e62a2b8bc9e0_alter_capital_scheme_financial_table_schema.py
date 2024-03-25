"""Alter capital scheme financial table schema

Revision ID: e62a2b8bc9e0
Revises: 0346163fa870
Create Date: 2024-03-25 16:37:57.133912

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "e62a2b8bc9e0"
down_revision: Union[str, None] = "0346163fa870"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme_financial SET SCHEMA capital_scheme")
    else:
        op.create_table(
            "capital_scheme_financial",
            sa.Column("capital_scheme_financial_id", sa.Integer, primary_key=True),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_financial_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("financial_type_id", sa.Integer, nullable=False),
            sa.Column("amount", sa.Integer, nullable=False),
            sa.Column("effective_date_from", sa.DateTime, nullable=False),
            sa.Column("effective_date_to", sa.DateTime),
            sa.Column("data_source_id", sa.Integer, nullable=False),
            schema="capital_scheme",
        )
        op.execute("INSERT INTO capital_scheme.capital_scheme_financial SELECT * FROM capital_scheme_financial")
        op.drop_table("capital_scheme_financial")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme.capital_scheme_financial SET SCHEMA public")
    else:
        op.create_table(
            "capital_scheme_financial",
            sa.Column("capital_scheme_financial_id", sa.Integer, primary_key=True),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_financial_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("financial_type_id", sa.Integer, nullable=False),
            sa.Column("amount", sa.Integer, nullable=False),
            sa.Column("effective_date_from", sa.DateTime, nullable=False),
            sa.Column("effective_date_to", sa.DateTime),
            sa.Column("data_source_id", sa.Integer, nullable=False),
        )
        op.execute("INSERT INTO capital_scheme_financial SELECT * FROM capital_scheme.capital_scheme_financial")
        op.drop_table("capital_scheme_financial", schema="capital_scheme")
