"""fix task_status enum - remove in_progress

Revision ID: b0483719d362
Revises: 351df5f712fe
Create Date: 2026-01-23 21:31:15.914533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0483719d362'
down_revision: Union[str, Sequence[str], None] = '351df5f712fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Convert to text (bypass enum)
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE text")
    
    # 2. Update data
    op.execute("UPDATE tasks SET status = 'in-progress' WHERE status = 'in_progress'")
    
    # 3. Drop old enum
    op.execute("DROP TYPE IF EXISTS task_status")
    
    # 4. Create new enum
    op.execute("CREATE TYPE task_status AS ENUM ('initialised', 'in-progress', 'completed')")
    
    # 5. Convert back to enum
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE task_status USING status::task_status")

def downgrade():
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE text")
    op.execute("DROP TYPE task_status")
    op.execute("CREATE TYPE task_status AS ENUM ('initialised', 'in_progress', 'in-progress', 'completed')")
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE task_status USING status::task_status")
