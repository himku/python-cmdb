"""init

Revision ID: a7f23d764d38
Revises: 
Create Date: 2025-07-23 17:45:31.217487

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import VARCHAR

# revision identifiers, used by Alembic.
revision = 'a7f23d764d38'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 用户表
    op.create_table(
        'users',
        sa.Column('id', VARCHAR(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('full_name', sa.String(100)),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # 角色表
    op.create_table(
        'roles',
        sa.Column('id', VARCHAR(36), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('description', sa.String(255)),
    )
    # 权限表
    op.create_table(
        'permissions',
        sa.Column('id', VARCHAR(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('code', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.String(255)),
    )
    # 用户-角色多对多
    op.create_table(
        'user_role',
        sa.Column('user_id', VARCHAR(36), sa.ForeignKey('users.id')),
        sa.Column('role_id', VARCHAR(36), sa.ForeignKey('roles.id')),
    )
    # 角色-权限多对多
    op.create_table(
        'role_permission',
        sa.Column('role_id', VARCHAR(36), sa.ForeignKey('roles.id')),
        sa.Column('permission_id', VARCHAR(36), sa.ForeignKey('permissions.id')),
    )
    # Casbin模型表
    op.create_table(
        'casbin_model',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('content', sa.Text, nullable=False, comment='Casbin模型内容')
    )

def downgrade():
    op.execute("DROP TABLE IF EXISTS casbin_model")
    op.execute("DROP TABLE IF EXISTS role_permission")
    op.execute("DROP TABLE IF EXISTS user_role")
    op.execute("DROP TABLE IF EXISTS permissions")
    op.execute("DROP TABLE IF EXISTS roles")
    op.execute("DROP TABLE IF EXISTS users")
