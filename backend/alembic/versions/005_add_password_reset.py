"""Add password reset fields to users

Revision ID: 005
Revises: 004
Create Date: 2026-06-24
"""
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users
        ADD COLUMN password_reset_token VARCHAR(128),
        ADD COLUMN password_reset_token_expires_at TIMESTAMP WITH TIME ZONE
    """)
    op.execute(
        "CREATE UNIQUE INDEX idx_users_password_reset_token ON users (password_reset_token) "
        "WHERE password_reset_token IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_users_password_reset_token")
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS password_reset_token,
        DROP COLUMN IF EXISTS password_reset_token_expires_at
    """)
