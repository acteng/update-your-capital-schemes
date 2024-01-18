"""Alter effective dates to datetime

Revision ID: b670e54fe7af
Revises: e621f3e86ba3
Create Date: 2024-01-18 17:45:52.388258

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b670e54fe7af"
down_revision: Union[str, None] = "e621f3e86ba3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("capital_scheme_financial") as batch_op:
        batch_op.alter_column("effective_date_from", type_=sa.DateTime)
        batch_op.alter_column("effective_date_to", type_=sa.DateTime)

    with op.batch_alter_table("scheme_milestone") as batch_op:
        batch_op.alter_column("effective_date_from", type_=sa.DateTime)
        batch_op.alter_column("effective_date_to", type_=sa.DateTime)

    with op.batch_alter_table("scheme_intervention") as batch_op:
        batch_op.alter_column("effective_date_from", type_=sa.DateTime)
        batch_op.alter_column("effective_date_to", type_=sa.DateTime)


def downgrade() -> None:
    with op.batch_alter_table("capital_scheme_financial") as batch_op:
        batch_op.alter_column("effective_date_from", type_=sa.Date)
        batch_op.alter_column("effective_date_to", type_=sa.Date)

    with op.batch_alter_table("scheme_milestone") as batch_op:
        batch_op.alter_column("effective_date_from", type_=sa.Date)
        batch_op.alter_column("effective_date_to", type_=sa.Date)

    with op.batch_alter_table("scheme_intervention") as batch_op:
        batch_op.alter_column("effective_date_from", type_=sa.Date)
        batch_op.alter_column("effective_date_to", type_=sa.Date)
