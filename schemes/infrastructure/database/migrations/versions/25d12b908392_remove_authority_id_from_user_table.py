"""Remove authority id from user table

Revision ID: 25d12b908392
Revises: 42d7a1652946
Create Date: 2025-04-01 17:45:21.540853

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "25d12b908392"
down_revision: Union[str, None] = "42d7a1652946"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_column("authority_id")


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column("authority_id", sa.Integer, nullable=False))
