"""Create capital scheme overview table

Revision ID: 3f8e2f1e7220
Revises: 3e6f6be8bf70
Create Date: 2024-07-15 11:36:09.766316

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "3f8e2f1e7220"
down_revision: Union[str, None] = "3e6f6be8bf70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capital_scheme_overview",
        sa.Column("capital_scheme_overview_id", sa.Integer, primary_key=True),
        sa.Column(
            "capital_scheme_id",
            sa.Integer,
            sa.ForeignKey(
                "capital_scheme.capital_scheme.capital_scheme_id", name="capital_scheme_overview_capital_scheme_id_fkey"
            ),
            nullable=False,
        ),
        sa.Column(
            "bid_submitting_authority_id",
            sa.Integer,
            sa.ForeignKey(
                "authority.authority.authority_id", name="capital_scheme_overview_bid_submitting_authority_id_fkey"
            ),
            nullable=False,
        ),
        sa.Column("effective_date_from", sa.DateTime, nullable=False),
        sa.Column("effective_date_to", sa.DateTime),
        schema="capital_scheme",
    )
    op.execute(
        """
        WITH earliest_bid_status AS
        (
            SELECT capital_scheme_id, min(effective_date_from) AS effective_date_from
            FROM capital_scheme.capital_scheme_bid_status
            GROUP BY capital_scheme_id
        )
        INSERT INTO capital_scheme.capital_scheme_overview
        (
            capital_scheme_id,
            bid_submitting_authority_id,
            effective_date_from
        )
        SELECT
            cs.capital_scheme_id,
            cs.bid_submitting_authority_id,
            earliest_bid_status.effective_date_from
        FROM capital_scheme.capital_scheme cs
        LEFT JOIN earliest_bid_status ON cs.capital_scheme_id = earliest_bid_status.capital_scheme_id;
        """
    )
    op.drop_column("capital_scheme", column_name="bid_submitting_authority_id", schema="capital_scheme")


def downgrade() -> None:
    op.add_column(
        "capital_scheme",
        column=sa.Column(
            "bid_submitting_authority_id",
            sa.Integer,
            sa.ForeignKey("authority.authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey"),
        ),
        schema="capital_scheme",
    )
    op.execute(
        """
        UPDATE capital_scheme.capital_scheme cs
        SET bid_submitting_authority_id = cso.bid_submitting_authority_id
        FROM capital_scheme.capital_scheme_overview cso
        WHERE cs.capital_scheme_id = cso.capital_scheme_id
        AND cso.effective_date_to IS NULL;
        """
    )
    with op.batch_alter_table("capital_scheme", schema="capital_scheme") as batch_op:
        batch_op.alter_column("bid_submitting_authority_id", nullable=False)
    op.drop_table("capital_scheme_overview", schema="capital_scheme")
