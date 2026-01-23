"""add_in_progress_status_to_task_status_enum

Revision ID: 351df5f712fe
Revises: a81f38abb0ec
Create Date: 2026-01-23 04:15:32.466469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '351df5f712fe'
down_revision: Union[str, Sequence[str], None] = 'a81f38abb0ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new enum value
    op.execute("ALTER TYPE task_status ADD VALUE IF NOT EXISTS 'in-progress'")

def downgrade():
    # Note: PostgreSQL doesn't support removing enum values easily
    # You would need to recreate the enum type
    pass
