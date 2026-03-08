"""Add authentication fields to users table

Revision ID: 002
Revises: 001
Create Date: 2026-03-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column with default 'viewer'
    op.add_column(
        'users',
        sa.Column('role', sa.String(), nullable=False, server_default='viewer')
    )
    
    # Add last_login column for tracking login timestamps
    op.add_column(
        'users',
        sa.Column('last_login', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    # Remove the columns
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'role')
