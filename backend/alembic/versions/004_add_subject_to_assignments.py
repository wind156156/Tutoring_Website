"""add subject column to assignments

Revision ID: 004
Revises: 003
Create Date: 2026-08-21
"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('assignments',
        sa.Column('subject', sa.String(50), nullable=False, server_default='')
    )


def downgrade():
    op.drop_column('assignments', 'subject')
