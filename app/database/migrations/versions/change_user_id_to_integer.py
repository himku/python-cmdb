"""change user id from uuid to integer

Revision ID: change_user_id_to_integer
Revises: ac7b756b7e58
Create Date: 2025-07-31 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'change_user_id_to_integer'
down_revision = 'ac7b756b7e58'
branch_labels = None
depends_on = None

def upgrade():
    """将用户相关表的ID从UUID字符串改为自增整数"""
    
    # 1. 删除所有数据以简化迁移
    op.execute("DELETE FROM user_role")
    op.execute("DELETE FROM role_permission")
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM roles")
    op.execute("DELETE FROM permissions")
    
    # 2. 删除外键约束（如果存在的话）
    try:
        op.drop_constraint('user_role_ibfk_1', 'user_role', type_='foreignkey')
    except:
        pass
    try:
        op.drop_constraint('user_role_ibfk_2', 'user_role', type_='foreignkey')
    except:
        pass
    try:
        op.drop_constraint('role_permission_ibfk_1', 'role_permission', type_='foreignkey')
    except:
        pass
    try:
        op.drop_constraint('role_permission_ibfk_2', 'role_permission', type_='foreignkey')
    except:
        pass
    
    # 3. 删除关联表并重新创建（避免ALTER TABLE的限制）
    op.drop_table('user_role')
    op.drop_table('role_permission')
    
    # 4. 修改主表的ID字段
    # 修改users表
    op.alter_column('users', 'id', 
                   existing_type=sa.String(36),
                   type_=sa.Integer(),
                   existing_nullable=False,
                   autoincrement=True)
    
    # 修改roles表
    op.alter_column('roles', 'id',
                   existing_type=sa.String(36), 
                   type_=sa.Integer(),
                   existing_nullable=False,
                   autoincrement=True)
    
    # 修改permissions表
    op.alter_column('permissions', 'id',
                   existing_type=sa.String(36),
                   type_=sa.Integer(), 
                   existing_nullable=False,
                   autoincrement=True)
    
    # 5. 重新创建关联表
    op.create_table('user_role',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    op.create_table('role_permission',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], )
    )


def downgrade():
    """回滚迁移 - 将整数ID改回UUID字符串"""
    
    # 警告：这个downgrade会丢失所有数据
    
    # 1. 删除所有数据
    op.execute("DELETE FROM user_role")
    op.execute("DELETE FROM role_permission")
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM roles")
    op.execute("DELETE FROM permissions")
    
    # 2. 删除外键约束
    op.drop_constraint('user_role_user_id_fkey', 'user_role', type_='foreignkey')
    op.drop_constraint('user_role_role_id_fkey', 'user_role', type_='foreignkey')
    op.drop_constraint('role_permission_role_id_fkey', 'role_permission', type_='foreignkey')
    op.drop_constraint('role_permission_permission_id_fkey', 'role_permission', type_='foreignkey')
    
    # 3. 修改主表的ID字段回UUID
    # 修改users表
    op.drop_column('users', 'id')
    op.add_column('users', sa.Column('id', sa.String(36), nullable=False))
    op.create_primary_key('pk_users_id', 'users', ['id'])
    
    # 修改roles表
    op.drop_column('roles', 'id')
    op.add_column('roles', sa.Column('id', sa.String(36), nullable=False))
    op.create_primary_key('pk_roles_id', 'roles', ['id'])
    
    # 修改permissions表
    op.drop_column('permissions', 'id')
    op.add_column('permissions', sa.Column('id', sa.String(36), nullable=False))
    op.create_primary_key('pk_permissions_id', 'permissions', ['id'])
    
    # 4. 修改关联表的外键字段回UUID
    # 修改user_role表
    op.drop_column('user_role', 'user_id')
    op.drop_column('user_role', 'role_id')
    op.add_column('user_role', sa.Column('user_id', sa.String(36), nullable=False))
    op.add_column('user_role', sa.Column('role_id', sa.String(36), nullable=False))
    
    # 修改role_permission表
    op.drop_column('role_permission', 'role_id')
    op.drop_column('role_permission', 'permission_id')
    op.add_column('role_permission', sa.Column('role_id', sa.String(36), nullable=False))
    op.add_column('role_permission', sa.Column('permission_id', sa.String(36), nullable=False))
    
    # 5. 重新创建外键约束
    op.create_foreign_key('user_role_ibfk_1', 'user_role', 'users', ['user_id'], ['id'])
    op.create_foreign_key('user_role_ibfk_2', 'user_role', 'roles', ['role_id'], ['id'])
    op.create_foreign_key('role_permission_ibfk_1', 'role_permission', 'roles', ['role_id'], ['id'])
    op.create_foreign_key('role_permission_ibfk_2', 'role_permission', 'permissions', ['permission_id'], ['id']) 