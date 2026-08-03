"""Add data source to scheme milestone table

Revision ID: e7053d7f92d2
Revises: b670e54fe7af
Create Date: 2024-02-02 12:56:25.647921

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e7053d7f92d2"
down_revision: str | None = "b670e54fe7af"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("scheme_milestone", sa.Column("data_source_id", sa.Integer, nullable=False))


def downgrade() -> None:
    op.drop_column("scheme_milestone", "data_source_id")
