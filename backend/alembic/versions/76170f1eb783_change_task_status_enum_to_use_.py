"""change task_status enum to use underscore

Revision ID: 76170f1eb783
Revises: b0483719d362
Create Date: 2026-01-24 02:21:20.724662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76170f1eb783'
down_revision: Union[str, Sequence[str], None] = 'b0483719d362'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE text USING status::text")
    
    op.execute("UPDATE tasks SET status = 'in_progress' WHERE status = 'in-progress'")
    
    op.execute("DROP TYPE task_status")
    op.execute("CREATE TYPE task_status AS ENUM ('initialised', 'in_progress', 'completed')")
    
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE task_status USING status::task_status")


def downgrade():
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE text USING status::text")
    op.execute("UPDATE tasks SET status = 'in-progress' WHERE status = 'in_progress'")
    op.execute("DROP TYPE task_status")
    op.execute("CREATE TYPE task_status AS ENUM ('initialised', 'in-progress', 'completed')")
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE task_status USING status::task_status")
