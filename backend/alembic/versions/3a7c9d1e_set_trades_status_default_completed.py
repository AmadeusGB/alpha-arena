"""set trades.status default completed and backfill

Revision ID: 3a7c9d1e
Revises: 2f6c1a9f
Create Date: 2025-10-28 03:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a7c9d1e'
down_revision = '2f6c1a9f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) 回填现有 NULL/空字符串为 completed
    op.execute("UPDATE trades SET status='completed' WHERE status IS NULL OR status='' ")
    # 2) 设置服务端默认值
    with op.batch_alter_table('trades') as batch_op:
        batch_op.alter_column('status', existing_type=sa.String(length=20), server_default='completed')


def downgrade() -> None:
    with op.batch_alter_table('trades') as batch_op:
        batch_op.alter_column('status', existing_type=sa.String(length=20), server_default=None)


