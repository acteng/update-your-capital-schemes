"""Alter capital scheme authority review table schema

Revision ID: 0346163fa870
Revises: 9d3defc17322
Create Date: 2024-03-25 16:28:33.543473

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "0346163fa870"
down_revision: Union[str, None] = "9d3defc17322"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme_authority_review SET SCHEMA capital_scheme")
    else:
        op.create_table(
            "capital_scheme_authority_review",
            sa.Column("capital_scheme_authority_review_id", sa.Integer, primary_key=True),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_authority_review_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("review_date", sa.DateTime, nullable=False),
            sa.Column("data_source_id", sa.Integer, nullable=False),
            schema="capital_scheme",
        )
        op.execute(
            "INSERT INTO capital_scheme.capital_scheme_authority_review SELECT * FROM capital_scheme_authority_review"
        )
        op.drop_table("capital_scheme_authority_review")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme.capital_scheme_authority_review SET SCHEMA public")
    else:
        op.create_table(
            "capital_scheme_authority_review",
            sa.Column("capital_scheme_authority_review_id", sa.Integer, primary_key=True),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_authority_review_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("review_date", sa.DateTime, nullable=False),
            sa.Column("data_source_id", sa.Integer, nullable=False),
        )
        op.execute(
            "INSERT INTO capital_scheme_authority_review SELECT * FROM capital_scheme.capital_scheme_authority_review"
        )
        op.drop_table("capital_scheme_authority_review", schema="capital_scheme")
