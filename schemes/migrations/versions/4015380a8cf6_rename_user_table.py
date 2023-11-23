"""Rename user table

Revision ID: 4015380a8cf6
Revises: bfc3cbc1bb13
Create Date: 2023-10-27 11:53:59.542995

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql.base import PGDialect

revision: str = "4015380a8cf6"
down_revision: Union[str, None] = "bfc3cbc1bb13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("users", "user")
    op.alter_column("user", "id", new_column_name="user_id")
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER SEQUENCE users_id_seq RENAME TO user_user_id_seq")


def downgrade() -> None:
    if op.get_context().dialect.name == PGDialect.name:
        op.execute("ALTER SEQUENCE user_user_id_seq RENAME TO users_id_seq")
    op.alter_column("user", "user_id", new_column_name="id")
    op.rename_table("user", "users")
