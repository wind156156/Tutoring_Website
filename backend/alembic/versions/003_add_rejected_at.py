"""add rejected_at to teachers

Revision ID: 003
Revises: ff9935732f2b
Create Date: 2026-08-21
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = 'ff9935732f2b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('teachers',
        sa.Column('rejected_at', sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column('teachers', 'rejected_at')
