"""add user_settings table

Revision ID: 004_user_settings
Revises: 003_chat_tables
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_user_settings'
down_revision = '003_chat_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_settings table
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('email_notifications', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('browser_notifications', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('task_reminders', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('dnd_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('dnd_start', sa.TIME(), nullable=True),
        sa.Column('dnd_end', sa.TIME(), nullable=True),
        sa.Column('theme', sa.String(length=50), nullable=True, server_default='dark'),
        sa.Column('font_size', sa.String(length=50), nullable=True, server_default='medium'),
        sa.Column('view_mode', sa.String(length=50), nullable=True, server_default='comfortable'),
        sa.Column('default_priority', sa.String(length=50), nullable=True, server_default='medium'),
        sa.Column('default_sort', sa.String(length=50), nullable=True, server_default='created_date'),
        sa.Column('show_completed', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create unique index on user_id
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'], unique=True)

    # Create foreign key constraint to user table
    op.create_foreign_key(
        'fk_user_settings_user_id',
        'user_settings',
        'user',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_user_settings_user_id', 'user_settings', type_='foreignkey')

    # Drop index
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')

    # Drop table
    op.drop_table('user_settings')
