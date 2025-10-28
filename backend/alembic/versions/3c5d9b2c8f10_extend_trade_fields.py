"""extend trade fields

Revision ID: 3c5d9b2c8f10
Revises: 0b2c1a7f4d92
Create Date: 2025-10-28 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c5d9b2c8f10'
down_revision = '0b2c1a7f4d92'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('trades', sa.Column('direction', sa.String(length=10), nullable=True))
    op.add_column('trades', sa.Column('leverage', sa.Float(), nullable=True))
    op.add_column('trades', sa.Column('close_price_upper', sa.Float(), nullable=True))
    op.add_column('trades', sa.Column('close_price_lower', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('trades', 'close_price_lower')
    op.drop_column('trades', 'close_price_upper')
    op.drop_column('trades', 'leverage')
    op.drop_column('trades', 'direction')


