"""add_trading_settings_table

Revision ID: 51f684e94cc3
Revises: ee69c297ab94
Create Date: 2025-10-27 15:43:33.255247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51f684e94cc3'
down_revision = 'ee69c297ab94'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('trading_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, server_default='default'),
        sa.Column('maker_fee', sa.Float(), nullable=True, server_default='0.0002'),
        sa.Column('taker_fee', sa.Float(), nullable=True, server_default='0.0004'),
        sa.Column('slippage', sa.Float(), nullable=True, server_default='0.0001'),
        sa.Column('max_leverage', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('allow_short', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('min_position', sa.Float(), nullable=True, server_default='0.001'),
        sa.Column('max_position', sa.Float(), nullable=True, server_default='0.2'),
        sa.Column('position_unit', sa.Float(), nullable=True, server_default='0.01'),
        sa.Column('stop_loss_min', sa.Float(), nullable=True, server_default='0.01'),
        sa.Column('stop_loss_max', sa.Float(), nullable=True, server_default='0.10'),
        sa.Column('take_profit_min', sa.Float(), nullable=True, server_default='0.01'),
        sa.Column('take_profit_max', sa.Float(), nullable=True, server_default='0.20'),
        sa.Column('max_position_percent', sa.Float(), nullable=True, server_default='0.8'),
        sa.Column('max_drawdown', sa.Float(), nullable=True, server_default='0.20'),
        sa.Column('min_confidence', sa.Float(), nullable=True, server_default='0.3'),
        sa.Column('max_open_positions', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('cooldown_minutes', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('min_trade_amount', sa.Float(), nullable=True, server_default='10.0'),
        sa.Column('max_trade_amount', sa.Float(), nullable=True, server_default='10000.0'),
        sa.Column('params', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade() -> None:
    op.drop_table('trading_settings')

