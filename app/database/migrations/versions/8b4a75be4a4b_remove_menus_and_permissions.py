
"""remove_menus_and_permissions

Revision ID: 8b4a75be4a4b
Revises: 2526fbf0a53a
Create Date: 2025-08-04 10:43:04.079734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b4a75be4a4b'
down_revision = '2526fbf0a53a'
branch_labels = None
depends_on = None

def upgrade():
    """删除菜单和权限相关的表"""
    # 1. 删除角色权限关联表（如果存在）
    try:
        op.drop_table('role_permission')
        print("✅ 删除 role_permission 表")
    except Exception as e:
        print(f"role_permission 表可能不存在: {e}")
    
    # 2. 删除权限表（如果存在）
    try:
        op.drop_table('permissions')
        print("✅ 删除 permissions 表")
    except Exception as e:
        print(f"permissions 表可能不存在: {e}")
    
    # 3. 删除菜单表
    try:
        op.drop_table('menus')
        print("✅ 删除 menus 表")
    except Exception as e:
        print(f"menus 表可能不存在: {e}")

def downgrade():
    """重新创建菜单表（仅菜单表，权限表不重新创建）"""
    # 只重新创建菜单表，因为我们要彻底移除权限系统
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
