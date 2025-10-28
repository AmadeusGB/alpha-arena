"""add trade feedback field

Revision ID: 2f6c1a9f
Revises: 9a2b4c6dadd1
Create Date: 2025-10-28 03:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f6c1a9f'
down_revision = '9a2b4c6dadd1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('trades', sa.Column('feedback', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('trades', 'feedback')


