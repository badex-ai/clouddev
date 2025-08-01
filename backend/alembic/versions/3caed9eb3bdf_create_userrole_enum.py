"""create_userrole_enum

Revision ID: 3caed9eb3bdf
Revises: 9c8e212f1566
Create Date: 2025-07-30 01:27:49.988994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3caed9eb3bdf'
down_revision: Union[str, Sequence[str], None] = '9c8e212f1566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    def upgrade():
    # Rename 'initialised' to 'initialized' in the enum type
        op.execute("ALTER TYPE task_status RENAME VALUE 'initialized' TO 'initialised'")
    


def downgrade() -> None:
    def downgrade():
    # Reverse the change
        op.execute("ALTER TYPE task_status RENAME VALUE 'initialiSed' TO 'initialized'")
    
