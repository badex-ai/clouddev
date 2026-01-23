"""fix_task_status_enum_to_hyphen

Revision ID: 2c4b22350669
Revises: 351df5f712fe
Create Date: 2026-01-23 17:18:55.950569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c4b22350669'
down_revision: Union[str, Sequence[str], None] = '351df5f712fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Simply rename the enum value - this automatically updates all data
    op.execute("ALTER TYPE task_status RENAME VALUE 'in_progress' TO 'in-progress'")


def downgrade():
    # Rename back to underscore version
    op.execute("ALTER TYPE task_status RENAME VALUE 'in-progress' TO 'in_progress'")
