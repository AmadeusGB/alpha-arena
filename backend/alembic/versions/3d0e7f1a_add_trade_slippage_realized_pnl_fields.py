"""add trade slippage and realized pnl fields

Revision ID: 3d0e7f1a
Revises: 3b9f2ed0
Create Date: 2025-10-28 05:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d0e7f1a'
down_revision = '3b9f2ed0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('trades') as batch_op:
        batch_op.add_column(sa.Column('slippage', sa.Float(), server_default='0.0'))
        batch_op.add_column(sa.Column('notional', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('margin_required', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('commission_rate', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('slippage_rate', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('realized_pnl', sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('trades') as batch_op:
        batch_op.drop_column('realized_pnl')
        batch_op.drop_column('slippage_rate')
        batch_op.drop_column('commission_rate')
        batch_op.drop_column('margin_required')
        batch_op.drop_column('notional')
        batch_op.drop_column('slippage')


