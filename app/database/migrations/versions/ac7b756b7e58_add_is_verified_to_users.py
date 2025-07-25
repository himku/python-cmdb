"""add is_verified to users

Revision ID: ac7b756b7e58
Revises: 0fcacaa6cba2
Create Date: 2025-07-25 16:17:28.446696

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ac7b756b7e58'
down_revision = '0fcacaa6cba2'
branch_labels = None
depends_on = None

def upgrade():
    # 新库已包含 is_verified 字段，跳过
    pass

def downgrade():
    pass
