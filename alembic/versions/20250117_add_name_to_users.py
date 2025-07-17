"""Add name field to users table

Revision ID: 20250117_add_name
Revises: 19ea266ff7b4
Create Date: 2025-01-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250117_add_name'
down_revision = '19ea266ff7b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name column to users table
    op.add_column('users', sa.Column('name', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove name column from users table
    op.drop_column('users', 'name')