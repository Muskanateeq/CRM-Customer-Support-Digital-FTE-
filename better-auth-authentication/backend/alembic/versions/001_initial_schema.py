"""
Initial database schema migration

Creates tables for:
- users (managed by Better Auth)
- tasks (with all fields for Basic + Intermediate + Advanced features)
- tags (user-specific tags)
- task_tags (junction table for many-to-many relationship)

Revision ID: 001
Create Date: 2026-02-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema"""

    # Create users table (managed by Better Auth)
    op.create_table(
        'users',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('completed', sa.Boolean, default=False, nullable=False),
        sa.Column('priority', sa.String(10), default='medium', nullable=False),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('due_time', sa.Time, nullable=True),
        sa.Column('recurrence_pattern', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("priority IN ('high', 'medium', 'low')", name='ck_task_priority'),
        sa.CheckConstraint("length(title) >= 1 AND length(title) <= 200", name='ck_task_title_length'),
    )

    # Create indexes for tasks table
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_completed', 'tasks', ['completed'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'])
    op.create_index('ix_tasks_user_completed', 'tasks', ['user_id', 'completed'])
    op.create_index('ix_tasks_user_due_date', 'tasks', ['user_id', 'due_date'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
    )
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])

    # Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer, sa.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.Integer, sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_index('ix_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('ix_task_tags_tag_id', 'task_tags', ['tag_id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('task_tags')
    op.drop_table('tags')
    op.drop_table('tasks')
    op.drop_table('users')
