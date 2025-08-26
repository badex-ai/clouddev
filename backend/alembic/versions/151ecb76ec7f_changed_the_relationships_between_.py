"""changed the relationships between models id to string

Revision ID: 151ecb76ec7f
Revises: 786cf28a3d99
Create Date: 2025-08-26 14:09:28.123050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '151ecb76ec7f'
down_revision: Union[str, Sequence[str], None] = '786cf28a3d99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a connection for raw SQL execution
    connection = op.get_bind()
    
    # Step 1: Add new temporary columns for the public_id relationships
    op.add_column('tasks', sa.Column('creator_public_id_temp', sa.String(36), nullable=True))
    op.add_column('tasks', sa.Column('assignee_public_id_temp', sa.String(36), nullable=True))
    op.add_column('tasks', sa.Column('family_public_id_temp', sa.String(36), nullable=True))
    op.add_column('users', sa.Column('family_public_id_temp', sa.String(36), nullable=True))
    
    # Step 2: Populate temporary columns with public_id values
    # Update tasks.creator_public_id_temp
    connection.execute(sa.text("""
        UPDATE tasks 
        SET creator_public_id_temp = users.public_id 
        FROM users 
        WHERE tasks.creator_id = users.id
    """))
    
    # Update tasks.assignee_public_id_temp
    connection.execute(sa.text("""
        UPDATE tasks 
        SET assignee_public_id_temp = users.public_id 
        FROM users 
        WHERE tasks.assignee_id = users.id
    """))
    
    # Update tasks.family_public_id_temp
    connection.execute(sa.text("""
        UPDATE tasks 
        SET family_public_id_temp = families.public_id 
        FROM families 
        WHERE tasks.family_id = families.id
    """))
    
    # Update users.family_public_id_temp
    connection.execute(sa.text("""
        UPDATE users 
        SET family_public_id_temp = families.public_id 
        FROM families 
        WHERE users.family_id = families.id
    """))
    
    # Step 3: Drop old foreign key constraints
    op.drop_constraint('tasks_creator_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tasks_assignee_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tasks_family_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('users_family_id_fkey', 'users', type_='foreignkey')
    
    # Step 4: Drop old columns
    op.drop_column('tasks', 'creator_id')
    op.drop_column('tasks', 'assignee_id')
    op.drop_column('tasks', 'family_id')
    op.drop_column('users', 'family_id')
    
    # Step 5: Rename temporary columns to final names
    op.alter_column('tasks', 'creator_public_id_temp', new_column_name='creator_id')
    op.alter_column('tasks', 'assignee_public_id_temp', new_column_name='assignee_id')
    op.alter_column('tasks', 'family_public_id_temp', new_column_name='family_id')
    op.alter_column('users', 'family_public_id_temp', new_column_name='family_id')
    
    # Step 6: Make columns not nullable
    op.alter_column('tasks', 'creator_id', nullable=False)
    op.alter_column('tasks', 'assignee_id', nullable=False)
    op.alter_column('tasks', 'family_id', nullable=False)
    op.alter_column('users', 'family_id', nullable=False)
    
    # Step 7: Add new foreign key constraints
    op.create_foreign_key('tasks_creator_id_fkey', 'tasks', 'users', ['creator_id'], ['public_id'])
    op.create_foreign_key('tasks_assignee_id_fkey', 'tasks', 'users', ['assignee_id'], ['public_id'])
    op.create_foreign_key('tasks_family_id_fkey', 'tasks', 'families', ['family_id'], ['public_id'])
    op.create_foreign_key('users_family_id_fkey', 'users', 'families', ['family_id'], ['public_id'])


def downgrade() -> None:
    # Reverse the process - convert back to integer foreign keys
    connection = op.get_bind()
    
    # Add temporary integer columns
    op.add_column('tasks', sa.Column('creator_id_temp', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('assignee_id_temp', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('family_id_temp', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('family_id_temp', sa.Integer(), nullable=True))
    
    # Populate with integer IDs
    connection.execute(sa.text("""
        UPDATE tasks 
        SET creator_id_temp = users.id 
        FROM users 
        WHERE tasks.creator_id = users.public_id
    """))
    
    connection.execute(sa.text("""
        UPDATE tasks 
        SET assignee_id_temp = users.id 
        FROM users 
        WHERE tasks.assignee_id = users.public_id
    """))
    
    connection.execute(sa.text("""
        UPDATE tasks 
        SET family_id_temp = families.id 
        FROM families 
        WHERE tasks.family_id = families.public_id
    """))
    
    connection.execute(sa.text("""
        UPDATE users 
        SET family_id_temp = families.id 
        FROM families 
        WHERE users.family_id = families.public_id
    """))
    
    # Drop public_id foreign key constraints
    op.drop_constraint('tasks_creator_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tasks_assignee_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tasks_family_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('users_family_id_fkey', 'users', type_='foreignkey')
    
    # Drop public_id columns
    op.drop_column('tasks', 'creator_id')
    op.drop_column('tasks', 'assignee_id')
    op.drop_column('tasks', 'family_id')
    op.drop_column('users', 'family_id')
    
    # Rename temp columns back
    op.alter_column('tasks', 'creator_id_temp', new_column_name='creator_id')
    op.alter_column('tasks', 'assignee_id_temp', new_column_name='assignee_id')
    op.alter_column('tasks', 'family_id_temp', new_column_name='family_id')
    op.alter_column('users', 'family_id_temp', new_column_name='family_id')
    
    # Make not nullable
    op.alter_column('tasks', 'creator_id', nullable=False)
    op.alter_column('tasks', 'assignee_id', nullable=False)
    op.alter_column('tasks', 'family_id', nullable=False)
    op.alter_column('users', 'family_id', nullable=False)
    
    # Recreate integer foreign key constraints
    op.create_foreign_key('tasks_creator_id_fkey', 'tasks', 'users', ['creator_id'], ['id'])
    op.create_foreign_key('tasks_assignee_id_fkey', 'tasks', 'users', ['assignee_id'], ['id'])
    op.create_foreign_key('tasks_family_id_fkey', 'tasks', 'families', ['family_id'], ['id'])
    op.create_foreign_key('users_family_id_fkey', 'users', 'families', ['family_id'], ['id'])