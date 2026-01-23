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
    # Check if 'in_progress' exists before renaming
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_enum e 
                JOIN pg_type t ON e.enumtypid = t.oid 
                WHERE t.typname = 'task_status' AND e.enumlabel = 'in_progress'
            ) THEN
                ALTER TYPE task_status RENAME VALUE 'in_progress' TO 'in-progress';
            END IF;
        END $$;
    """)

def downgrade():
    # Check if 'in-progress' exists before renaming back
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_enum e 
                JOIN pg_type t ON e.enumtypid = t.oid 
                WHERE t.typname = 'task_status' AND e.enumlabel = 'in-progress'
            ) THEN
                ALTER TYPE task_status RENAME VALUE 'in-progress' TO 'in_progress';
            END IF;
        END $$;
    """)
