"""Add scheme type to scheme table

Revision ID: 7ef68e039c47
Revises: db4f6a210831
Create Date: 2023-11-09 12:53:12.700816

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7ef68e039c47"
down_revision: Union[str, None] = "db4f6a210831"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("capital_scheme", sa.Column("scheme_type_id", sa.Integer))


def downgrade() -> None:
    op.drop_column("capital_scheme", "scheme_type_id")
