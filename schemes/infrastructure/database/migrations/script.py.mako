"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = ${repr(up_revision).replace("'", '"')}
down_revision: Union[str, None] = ${repr(down_revision).replace("'", '"')}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels).replace("'", '"')}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on).replace("'", '"')}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
