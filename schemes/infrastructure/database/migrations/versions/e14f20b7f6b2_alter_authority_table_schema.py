"""Alter authority table schema

Revision ID: e14f20b7f6b2
Revises: 484104648b2b
Create Date: 2024-03-22 17:36:41.175364

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "e14f20b7f6b2"
down_revision: Union[str, None] = "484104648b2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("CREATE SCHEMA authority")
        op.execute("ALTER TABLE authority SET SCHEMA authority")
    else:
        op.execute("ATTACH DATABASE ':memory:' AS authority")

        op.create_table(
            "authority",
            sa.Column("authority_id", sa.Integer, primary_key=True),
            sa.Column("authority_full_name", sa.Text, nullable=False),
            schema="authority",
        )
        op.execute("INSERT INTO authority.authority SELECT * FROM authority")

        with op.batch_alter_table("user") as batch_op:
            batch_op.drop_constraint("user_authority_id_fkey")
            batch_op.create_foreign_key(
                "user_authority_id_fkey", "authority", ["authority_id"], ["authority_id"], referent_schema="authority"
            )

        with op.batch_alter_table("capital_scheme") as batch_op:
            batch_op.drop_constraint("capital_scheme_bid_submitting_authority_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_bid_submitting_authority_id_fkey",
                "authority",
                ["bid_submitting_authority_id"],
                ["authority_id"],
                referent_schema="authority",
            )

        op.drop_table("authority")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER TABLE authority.authority SET SCHEMA public")
        op.execute("DROP SCHEMA authority")
    else:
        op.create_table(
            "authority",
            sa.Column("authority_id", sa.Integer, primary_key=True),
            sa.Column("authority_full_name", sa.Text, nullable=False),
        )
        op.execute("INSERT INTO authority SELECT * FROM authority.authority")

        with op.batch_alter_table("user") as batch_op:
            batch_op.drop_constraint("user_authority_id_fkey")
            batch_op.create_foreign_key("user_authority_id_fkey", "authority", ["authority_id"], ["authority_id"])

        with op.batch_alter_table("capital_scheme") as batch_op:
            batch_op.drop_constraint("capital_scheme_bid_submitting_authority_id_fkey")
            batch_op.create_foreign_key(
                "capital_scheme_bid_submitting_authority_id_fkey",
                "authority",
                ["bid_submitting_authority_id"],
                ["authority_id"],
            )

        op.drop_table("authority", schema="authority")

        op.execute("DETACH DATABASE authority")
