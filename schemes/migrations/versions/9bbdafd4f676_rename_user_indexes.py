"""Rename user indexes

Revision ID: 9bbdafd4f676
Revises: 4015380a8cf6
Create Date: 2023-10-30 14:40:39.757844

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9bbdafd4f676"
down_revision: Union[str, None] = "4015380a8cf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name == "postgresql":
        op.drop_constraint("users_pkey", "user")
        op.create_primary_key("user_pkey", "user", ["user_id"])
        op.drop_constraint("users_email_key", "user")
        op.create_unique_constraint("user_email_key", "user", ["email"])


def downgrade() -> None:
    if op.get_context().dialect.name == "postgresql":
        op.drop_constraint("user_email_key", "user")
        op.create_unique_constraint("users_email_key", "user", ["email"])
        op.drop_constraint("user_pkey", "user")
        op.create_primary_key("users_pkey", "user", ["user_id"])
