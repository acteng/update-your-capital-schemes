"""Alter scheme intervention value nullable

Revision ID: 55d82155e1d2
Revises: 128d4081b36d
Create Date: 2023-12-15 17:41:54.857394

"""
from typing import Sequence, Union

from alembic import op

revision: str = "55d82155e1d2"
down_revision: Union[str, None] = "128d4081b36d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("scheme_intervention") as batch_op:
        batch_op.alter_column("intervention_value", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("scheme_intervention") as batch_op:
        batch_op.alter_column("intervention_value", nullable=True)
