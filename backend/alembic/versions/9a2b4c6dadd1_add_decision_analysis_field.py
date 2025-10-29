"""add analysis to decisions

Revision ID: 9a2b4c6dadd1
Revises: 7d1b3c4e1f21
Create Date: 2025-10-28 02:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a2b4c6dadd1'
down_revision = '7d1b3c4e1f21'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('decisions', sa.Column('analysis', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('decisions', 'analysis')


