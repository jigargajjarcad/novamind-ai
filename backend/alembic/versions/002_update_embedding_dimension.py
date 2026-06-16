"""Update embedding dimension from 1536 to 1024 (voyage-3 model output)

Revision ID: 002
Revises: 001
Create Date: 2026-06-16
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Must drop the hnsw index before altering vector dimension
    op.execute("DROP INDEX IF EXISTS chunk_embeddings_embedding_idx")
    op.execute("ALTER TABLE chunk_embeddings ALTER COLUMN embedding TYPE vector(1024)")
    op.execute("CREATE INDEX ON chunk_embeddings USING hnsw (embedding vector_cosine_ops)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS chunk_embeddings_embedding_idx")
    op.execute("ALTER TABLE chunk_embeddings ALTER COLUMN embedding TYPE vector(1536)")
    op.execute("CREATE INDEX ON chunk_embeddings USING hnsw (embedding vector_cosine_ops)")
