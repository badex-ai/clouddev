"""changed the in initialized value to initialised

Revision ID: d37c8d6c3ac6
Revises: 3caed9eb3bdf
Create Date: 2025-07-30 02:32:24.073817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd37c8d6c3ac6'
down_revision: Union[str, Sequence[str], None] = '3caed9eb3bdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
