"""add casbin_model table

Revision ID: casbinmodel001
Revises: 
Create Date: 2025-07-23 17:58:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'casbinmodel001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'casbin_model',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('content', sa.Text, nullable=False, comment='Casbin模型内容')
    )

def downgrade():
    op.drop_table('casbin_model')
