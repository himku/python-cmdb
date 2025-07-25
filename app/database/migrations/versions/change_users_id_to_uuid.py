"""change users.id from int to uuid

Revision ID: change_users_id_to_uuid
Revises: ac7b756b7e58
Create Date: 2025-07-25 16:28:20.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = 'change_users_id_to_uuid'
down_revision = 'ac7b756b7e58'
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
