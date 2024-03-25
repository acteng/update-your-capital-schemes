"""Alter capital scheme intervention table schema

Revision ID: b20fe2fa94f9
Revises: e62a2b8bc9e0
Create Date: 2024-03-25 16:41:01.316445

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "b20fe2fa94f9"
down_revision: Union[str, None] = "e62a2b8bc9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme_intervention SET SCHEMA capital_scheme")
    else:
        op.create_table(
            "capital_scheme_intervention",
            sa.Column("capital_scheme_intervention_id", sa.Integer, primary_key=True),
            sa.Column("intervention_type_measure_id", sa.Integer, nullable=False),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_intervention_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("intervention_value", sa.Numeric(precision=15, scale=6), nullable=False),
            sa.Column("observation_type_id", sa.Integer, nullable=False),
            sa.Column("effective_date_from", sa.DateTime, nullable=False),
            sa.Column("effective_date_to", sa.DateTime),
            schema="capital_scheme",
        )
        op.execute("INSERT INTO capital_scheme.capital_scheme_intervention SELECT * FROM capital_scheme_intervention")
        op.drop_table("capital_scheme_intervention")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE capital_scheme.capital_scheme_intervention SET SCHEMA public")
    else:
        op.create_table(
            "capital_scheme_intervention",
            sa.Column("capital_scheme_intervention_id", sa.Integer, primary_key=True),
            sa.Column("intervention_type_measure_id", sa.Integer, nullable=False),
            sa.Column(
                "capital_scheme_id",
                sa.Integer,
                sa.ForeignKey(
                    "capital_scheme.capital_scheme.capital_scheme_id",
                    name="capital_scheme_intervention_capital_scheme_id_fkey",
                ),
                nullable=False,
            ),
            sa.Column("intervention_value", sa.Numeric(precision=15, scale=6), nullable=False),
            sa.Column("observation_type_id", sa.Integer, nullable=False),
            sa.Column("effective_date_from", sa.DateTime, nullable=False),
            sa.Column("effective_date_to", sa.DateTime),
        )
        op.execute("INSERT INTO capital_scheme_intervention SELECT * FROM capital_scheme.capital_scheme_intervention")
        op.drop_table("capital_scheme_intervention", schema="capital_scheme")
