"""add decision.status and decision.feedback

Revision ID: 3b9f2ed0
Revises: 3a7c9d1e
Create Date: 2025-10-28 04:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b9f2ed0'
down_revision = '3a7c9d1e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('decisions') as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), server_default='pending'))
        batch_op.add_column(sa.Column('feedback', sa.Text()))


def downgrade() -> None:
    with op.batch_alter_table('decisions') as batch_op:
        batch_op.drop_column('feedback')
        batch_op.drop_column('status')


