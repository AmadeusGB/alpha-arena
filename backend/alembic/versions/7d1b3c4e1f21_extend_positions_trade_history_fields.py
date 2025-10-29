"""extend positions trade history fields

Revision ID: 7d1b3c4e1f21
Revises: 3c5d9b2c8f10
Create Date: 2025-10-28 01:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d1b3c4e1f21'
down_revision = '3c5d9b2c8f10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # positions
    op.add_column('positions', sa.Column('side', sa.String(length=10), nullable=True))
    op.add_column('positions', sa.Column('leverage', sa.Float(), nullable=True))
    op.add_column('positions', sa.Column('margin', sa.Float(), nullable=True))

    # trades
    op.add_column('trades', sa.Column('action_type', sa.String(length=20), nullable=True))

    # portfolio_history
    op.add_column('portfolio_history', sa.Column('long_exposure', sa.Float(), nullable=True))
    op.add_column('portfolio_history', sa.Column('short_exposure', sa.Float(), nullable=True))
    op.add_column('portfolio_history', sa.Column('total_quantity', sa.Float(), nullable=True))
    op.add_column('portfolio_history', sa.Column('avg_leverage', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('portfolio_history', 'avg_leverage')
    op.drop_column('portfolio_history', 'total_quantity')
    op.drop_column('portfolio_history', 'short_exposure')
    op.drop_column('portfolio_history', 'long_exposure')
    op.drop_column('trades', 'action_type')
    op.drop_column('positions', 'margin')
    op.drop_column('positions', 'leverage')
    op.drop_column('positions', 'side')


