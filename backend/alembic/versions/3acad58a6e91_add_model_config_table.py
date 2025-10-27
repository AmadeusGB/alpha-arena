"""add_model_config_table

Revision ID: 3acad58a6e91
Revises: 51f684e94cc3
Create Date: 2025-10-27 15:46:55.307515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3acad58a6e91'
down_revision = '51f684e94cc3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('model_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='siliconflow'),
        sa.Column('model_id', sa.String(length=100), nullable=False),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('base_url', sa.String(length=255), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True, server_default='200'),
        sa.Column('temperature', sa.Float(), nullable=True, server_default='0.1'),
        sa.Column('timeout', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_test_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_test_result', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('test_error', sa.String(length=500), nullable=True),
        sa.Column('total_calls', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('success_calls', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('fail_calls', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_response_time', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('params', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade() -> None:
    op.drop_table('model_configs')

