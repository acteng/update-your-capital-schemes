"""Add funding programme to scheme table

Revision ID: f0073277add0
Revises: 7ef68e039c47
Create Date: 2023-11-10 15:11:59.019108

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f0073277add0"
down_revision: Union[str, None] = "7ef68e039c47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("capital_scheme", sa.Column("funding_programme_id", sa.Integer))


def downgrade() -> None:
    op.drop_column("capital_scheme", "funding_programme_id")
