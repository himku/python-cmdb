
"""add menu table

Revision ID: 2526fbf0a53a
Revises: change_user_id_to_integer
Create Date: 2025-07-31 14:45:32.127467

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2526fbf0a53a'
down_revision = 'change_user_id_to_integer'
branch_labels = None
depends_on = None

def upgrade():
    """只添加菜单表"""
    # 创建菜单表
    op.create_table('menus',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='菜单名称'),
        sa.Column('title', sa.String(length=100), nullable=False, comment='菜单标题(显示名称)'),
        sa.Column('path', sa.String(length=255), nullable=True, comment='路由路径'),
        sa.Column('component', sa.String(length=255), nullable=True, comment='组件路径'),
        sa.Column('redirect', sa.String(length=255), nullable=True, comment='重定向地址'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父菜单ID'),
        sa.Column('sort', sa.Integer(), nullable=True, default=0, comment='排序序号'),
        sa.Column('level', sa.Integer(), nullable=True, default=1, comment='菜单层级'),
        sa.Column('menu_type', sa.Integer(), nullable=True, default=1, comment='菜单类型: 1-目录 2-菜单 3-按钮'),
        sa.Column('is_visible', sa.Boolean(), nullable=True, default=True, comment='是否显示'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, default=True, comment='是否启用'),
        sa.Column('is_cache', sa.Boolean(), nullable=True, default=False, comment='是否缓存'),
        sa.Column('is_frame', sa.Boolean(), nullable=True, default=False, comment='是否为外链'),
        sa.Column('icon', sa.String(length=100), nullable=True, comment='菜单图标'),
        sa.Column('icon_type', sa.Integer(), nullable=True, default=1, comment='图标类型'),
        sa.Column('permission_code', sa.String(length=100), nullable=True, comment='权限标识码'),
        sa.Column('meta', sa.Text(), nullable=True, comment='元数据配置'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['menus.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    """删除菜单表"""
    op.drop_table('menus')
