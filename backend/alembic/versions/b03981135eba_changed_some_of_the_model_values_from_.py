"""changed some of the model values from optional to required

Revision ID: b03981135eba
Revises: 71fb60f2d68f
Create Date: 2025-08-01 18:31:28.322071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b03981135eba'
down_revision: Union[str, Sequence[str], None] = '71fb60f2d68f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE userrole_new AS ENUM('admin', 'member')")

    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole_new USING role::text::userrole_new" )

    op.execute("DROP TYPE userrole")

    op.execute("ALTER TYPE userrole_new RENAME TO userrole")


def downgrade() -> None:

    op.execute("CREATE TYPE userrole_old AS ENUM('ADMIN', 'MEMBER')")

    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole_old USING role::text::userrole_old")

    op.execute("DROP TYPE userrole")

    op.execute("ALTER TYPE userrole_old RENAME TO userrole")
