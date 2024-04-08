"""Alter capital scheme financial amount integer

Revision ID: e621f3e86ba3
Revises: 55d82155e1d2
Create Date: 2024-01-10 17:45:35.550159

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e621f3e86ba3"
down_revision: Union[str, None] = "55d82155e1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("capital_scheme_financial") as batch_op:
        batch_op.alter_column("amount", type_=sa.Integer)


def downgrade() -> None:
    with op.batch_alter_table("capital_scheme_financial") as batch_op:
        batch_op.alter_column("amount", type_=sa.Numeric)
