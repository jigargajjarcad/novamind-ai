"""Add email verification fields to users

Revision ID: 003
Revises: 002
Create Date: 2026-06-16
"""
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users
        ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE,
        ADD COLUMN verification_token VARCHAR(128),
        ADD COLUMN verification_token_expires_at TIMESTAMP WITH TIME ZONE
    """)
    op.execute(
        "CREATE UNIQUE INDEX idx_users_verification_token ON users (verification_token) "
        "WHERE verification_token IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_users_verification_token")
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS is_verified,
        DROP COLUMN IF EXISTS verification_token,
        DROP COLUMN IF EXISTS verification_token_expires_at
    """)
