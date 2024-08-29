"""Alter authority full name unique

Revision ID: 41d056f8ea12
Revises: 018d6bc92d76
Create Date: 2024-08-29 17:47:59.197504

"""

from typing import Sequence, Union

from alembic import op

revision: str = "41d056f8ea12"
down_revision: Union[str, None] = "018d6bc92d76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("authority", schema="authority") as batch_op:
        batch_op.create_unique_constraint("authority_authority_full_name_key", ["authority_full_name"])


def downgrade() -> None:
    with op.batch_alter_table("authority", schema="authority") as batch_op:
        batch_op.drop_constraint("authority_authority_full_name_key")
