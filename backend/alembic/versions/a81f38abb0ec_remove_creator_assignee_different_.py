"""remove creator_assignee_different constraint

Revision ID: a81f38abb0ec
Revises: 4172b2342ff7
Create Date: 2026-01-19 17:42:04.769705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'a81f38abb0ec'
down_revision: Union[str, Sequence[str], None] = '4172b2342ff7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Check if constraint exists before dropping (handles both local and AWS databases)
    conn = op.get_bind()
    result = conn.execute(text("""
        SELECT 1 FROM pg_constraint
        WHERE conname = 'creator_assignee_different'
        AND conrelid = 'tasks'::regclass
    """))
    if result.fetchone():
        op.drop_constraint('creator_assignee_different', 'tasks', type_='check')


def downgrade():
    op.create_check_constraint('creator_assignee_different', 'tasks', 'creator_id != assignee_id')