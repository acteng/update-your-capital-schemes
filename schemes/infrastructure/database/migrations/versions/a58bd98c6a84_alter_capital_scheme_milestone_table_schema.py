"""Alter capital scheme milestone table schema

Revision ID: a58bd98c6a84
Revises: b20fe2fa94f9
Create Date: 2024-03-25 16:43:56.163524

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "a58bd98c6a84"
down_revision: Union[str, None] = "b20fe2fa94f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme_milestone SET SCHEMA capital_scheme")
    else:
        op.create_table(
            "capital_scheme_milestone",
            sa.Column("capital_scheme_milestone_id", sa.Integer, primary_key=True),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_milestone_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("milestone_id", sa.Integer, nullable=False),
            sa.Column("status_date", sa.Date, nullable=False),
            sa.Column("observation_type_id", sa.Integer, nullable=False),
            sa.Column("effective_date_from", sa.DateTime, nullable=False),
            sa.Column("effective_date_to", sa.DateTime),
            sa.Column("data_source_id", sa.Integer, nullable=False),
            schema="capital_scheme",
        )
        op.execute("INSERT INTO capital_scheme.capital_scheme_milestone SELECT * FROM capital_scheme_milestone")
        op.drop_table("capital_scheme_milestone")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme.capital_scheme_milestone SET SCHEMA public")
    else:
        op.create_table(
            "capital_scheme_milestone",
            sa.Column("capital_scheme_milestone_id", sa.Integer, primary_key=True),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_milestone_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("milestone_id", sa.Integer, nullable=False),
            sa.Column("status_date", sa.Date, nullable=False),
            sa.Column("observation_type_id", sa.Integer, nullable=False),
            sa.Column("effective_date_from", sa.DateTime, nullable=False),
            sa.Column("effective_date_to", sa.DateTime),
            sa.Column("data_source_id", sa.Integer, nullable=False),
        )
        op.execute("INSERT INTO capital_scheme_milestone SELECT * FROM capital_scheme.capital_scheme_milestone")
        op.drop_table("capital_scheme_milestone", schema="capital_scheme")
