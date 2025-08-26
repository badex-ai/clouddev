"""added a new public id , added the is_active and is_deleted to user and task models

Revision ID: 786cf28a3d99
Revises: b03981135eba
Create Date: 2025-08-25 15:10:14.791665

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '786cf28a3d99'
down_revision: Union[str, Sequence[str], None] = 'b03981135eba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def add_public_id_to_table(table_name: str):
    """
    Add public_id column to a table with existing data.
    This follows the standard 3-step process for adding non-nullable columns.
    """
    # Step 1: Add column as nullable first
    op.add_column(
        table_name, 
        sa.Column('public_id', sa.String(length=36), nullable=True, unique=True, index=True)
    )
    op.add_column(
        table_name,
        sa.Column('is_deleted', sa.Boolean(), nullable=True)
    )
    
    # Step 2: Fill existing rows with generated UUIDs
    conn = op.get_bind()
    # Get all existing rows
    result = conn.execute(sa.text(f"SELECT id FROM {table_name}"))
    rows = result.fetchall()

    # Replace NULLs with some default family_id (must exist in families table!)
    conn.execute(sa.text("UPDATE tasks SET family_id = 3 WHERE family_id IS NULL"))

    conn.execute(sa.text("UPDATE users SET family_id = 3 WHERE family_id IS NULL"))
    
    for row in rows:
        conn.execute(
            sa.text(f"UPDATE {table_name} SET public_id = :pid, is_deleted = :deleted WHERE id = :id"),
            {"pid": str(uuid.uuid4()),"deleted": False, "id": row.id}
        )
    
    # Step 3: Alter column to make it non-nullable
    op.alter_column(table_name, 'public_id', nullable=False)
    op.alter_column(table_name, 'is_deleted', nullable=False)
    


def upgrade() -> None:
    """Upgrade schema."""
    
    # PHASE 1: Add public_id columns with proper 3-step process
    tables_to_update = ['families', 'tasks', 'users']
    for table_name in tables_to_update:
        add_public_id_to_table(table_name)
    
    # PHASE 2: Complete the rest of the original migration operations
    
    # Families table operations
    op.drop_constraint(op.f('families_name_key'), 'families', type_='unique')
    
    # Tasks table operations
    # op.add_column('tasks', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.alter_column('tasks', 'family_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('tasks', 'due_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    
    # Users table operations
    op.alter_column('users', 'family_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_index(op.f('ix_users_username'), table_name='users')


def downgrade() -> None:
    """Downgrade schema."""
    
    # Reverse users operations
    op.drop_index(op.f('ix_users_public_id'), table_name='users')
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.alter_column('users', 'family_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('users', 'public_id')
    
    # Reverse tasks operations
    op.drop_index(op.f('ix_tasks_public_id'), table_name='tasks')
    op.alter_column('tasks', 'due_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('tasks', 'family_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('tasks', 'is_deleted')
    op.drop_column('tasks', 'public_id')
    
    # Reverse families operations
    op.drop_index(op.f('ix_families_public_id'), table_name='families')
    op.create_unique_constraint(op.f('families_name_key'), 'families', ['name'], postgresql_nulls_not_distinct=False)
    op.drop_column('families', 'public_id')