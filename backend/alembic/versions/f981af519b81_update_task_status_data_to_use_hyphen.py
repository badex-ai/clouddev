"""update task status data to use hyphen

Revision ID: f981af519b81
Revises: 2c4b22350669
Create Date: 2026-01-23 17:54:49.665427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f981af519b81'
down_revision: Union[str, Sequence[str], None] = '2c4b22350669'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Just update the data - 'in-progress' enum value already exists
    op.execute("""
        UPDATE tasks 
        SET status = 'in-progress' 
        WHERE status = 'in_progress'
    """)


def downgrade():
    # Revert back to underscore
    op.execute("""
        UPDATE tasks 
        SET status = 'in_progress' 
        WHERE status = 'in-progress'
    """)
