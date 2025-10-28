"""add trading params to model_config

Revision ID: 0b2c1a7f4d92
Revises: 3acad58a6e91
Create Date: 2025-10-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b2c1a7f4d92'
down_revision = 'b971dbc637c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('model_configs', sa.Column('trade_symbol', sa.String(length=50), nullable=True))
    op.add_column('model_configs', sa.Column('trade_quantity', sa.Float(), nullable=True))
    op.add_column('model_configs', sa.Column('leverage', sa.Integer(), nullable=True))
    op.add_column('model_configs', sa.Column('trade_side', sa.String(length=10), nullable=True))
    op.add_column('model_configs', sa.Column('close_price_upper', sa.Float(), nullable=True))
    op.add_column('model_configs', sa.Column('close_price_lower', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('model_configs', 'close_price_lower')
    op.drop_column('model_configs', 'close_price_upper')
    op.drop_column('model_configs', 'trade_side')
    op.drop_column('model_configs', 'leverage')
    op.drop_column('model_configs', 'trade_quantity')
    op.drop_column('model_configs', 'trade_symbol')


