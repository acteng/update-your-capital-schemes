"""Add authority to user table

Revision ID: b0244825d57f
Revises: ecb44674a1da
Create Date: 2023-10-27 16:46:01.771963

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b0244825d57f"
down_revision: Union[str, None] = "ecb44674a1da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(
            sa.Column(
                "authority_id",
                sa.Integer,
                sa.ForeignKey("authority.authority_id", name="user_authority_id_fkey"),
                nullable=False,
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_constraint("user_authority_id_fkey")
        batch_op.drop_column("authority_id")
