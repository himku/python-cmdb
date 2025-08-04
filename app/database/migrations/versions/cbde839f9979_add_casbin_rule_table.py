
"""add_casbin_rule_table

Revision ID: cbde839f9979
Revises: 8b4a75be4a4b
Create Date: 2025-08-04 11:04:29.486749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbde839f9979'
down_revision = '8b4a75be4a4b'
branch_labels = None
depends_on = None

def upgrade():
    """创建 Casbin 策略表"""
    op.create_table('casbin_rule',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ptype', sa.String(length=255), nullable=False, comment='策略类型'),
        sa.Column('v0', sa.String(length=255), nullable=True, comment='主体/角色'),
        sa.Column('v1', sa.String(length=255), nullable=True, comment='对象/资源'),
        sa.Column('v2', sa.String(length=255), nullable=True, comment='动作/操作'),
        sa.Column('v3', sa.String(length=255), nullable=True, comment='扩展字段'),
        sa.Column('v4', sa.String(length=255), nullable=True, comment='扩展字段'),
        sa.Column('v5', sa.String(length=255), nullable=True, comment='扩展字段'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引以提高查询性能
    op.create_index('idx_casbin_rule_ptype', 'casbin_rule', ['ptype'])
    op.create_index('idx_casbin_rule_v0', 'casbin_rule', ['v0'])
    op.create_index('idx_casbin_rule_v1', 'casbin_rule', ['v1'])

def downgrade():
    """删除 Casbin 策略表"""
    op.drop_index('idx_casbin_rule_v1', table_name='casbin_rule')
    op.drop_index('idx_casbin_rule_v0', table_name='casbin_rule')
    op.drop_index('idx_casbin_rule_ptype', table_name='casbin_rule')
    op.drop_table('casbin_rule')
