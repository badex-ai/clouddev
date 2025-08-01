"""changed the status from initialized to initialised

Revision ID: 5b7889716cf6
Revises: d37c8d6c3ac6
Create Date: 2025-07-31 16:14:51.901829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b7889716cf6'
down_revision: Union[str, Sequence[str], None] = 'd37c8d6c3ac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE task_status_new AS ENUM('initialised', 'in-progress', 'completed')")

    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE task_status_new USING status::text::task_status_new" )

    op.execute("DROP TYPE task_status")

    op.execute("ALTER TYPE task_status_new RENAME TO task_status")


def downgrade() -> None:
    op.execute("CREATE TYPE task_status_old as ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED')")

    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE task_status_old USING status::text::task_status_old ")

    op.execute("DROP TYPE task_status")

    op.execute("ALTER TYPE task_status_old RENAME TO task_status")
