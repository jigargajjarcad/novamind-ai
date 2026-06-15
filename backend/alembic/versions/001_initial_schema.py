"""Initial schema — all tables

Revision ID: 001
Revises:
Create Date: 2026-06-15
"""
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_users_email ON users (email)")

    op.execute("""
        CREATE TABLE collections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_collections_user_id ON collections (user_id)")

    op.execute("""
        CREATE TABLE documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            filename VARCHAR(500) NOT NULL,
            file_size_bytes BIGINT,
            page_count INTEGER,
            status VARCHAR(50) DEFAULT 'pending',
            error_message TEXT,
            uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            processed_at TIMESTAMP WITH TIME ZONE
        )
    """)
    op.execute("CREATE INDEX idx_documents_collection_id ON documents (collection_id)")
    op.execute("CREATE INDEX idx_documents_user_id ON documents (user_id)")
    op.execute("CREATE INDEX idx_documents_status ON documents (status)")

    op.execute("""
        CREATE TABLE document_chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            page_number INTEGER,
            char_start INTEGER,
            char_end INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_document_chunks_document_id ON document_chunks (document_id)")

    op.execute("""
        CREATE TABLE chunk_embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            chunk_id UUID REFERENCES document_chunks(id) ON DELETE CASCADE,
            embedding vector(1536) NOT NULL,
            model_used VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_chunk_embeddings_chunk_id ON chunk_embeddings (chunk_id)")
    op.execute("CREATE INDEX ON chunk_embeddings USING hnsw (embedding vector_cosine_ops)")

    op.execute("""
        CREATE TABLE chat_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            collection_id UUID REFERENCES collections(id) ON DELETE SET NULL,
            name VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_chat_sessions_user_id ON chat_sessions (user_id)")

    op.execute("""
        CREATE TABLE chat_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_chat_messages_session_id ON chat_messages (session_id)")

    op.execute("""
        CREATE TABLE message_citations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            message_id UUID REFERENCES chat_messages(id) ON DELETE CASCADE,
            chunk_id UUID REFERENCES document_chunks(id) ON DELETE CASCADE,
            relevance_score FLOAT,
            citation_index INTEGER
        )
    """)
    op.execute("CREATE INDEX idx_message_citations_message_id ON message_citations (message_id)")

    op.execute("""
        CREATE TABLE query_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
            query TEXT NOT NULL,
            chunks_retrieved INTEGER,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost_usd DECIMAL(10, 6),
            latency_ms INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_query_logs_user_id ON query_logs (user_id)")
    op.execute("CREATE INDEX idx_query_logs_created_at ON query_logs (created_at)")

    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    for table in ("users", "collections", "chat_sessions"):
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)


def downgrade() -> None:
    for table in ("users", "collections", "chat_sessions"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table}")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column")

    op.execute("DROP TABLE IF EXISTS query_logs")
    op.execute("DROP TABLE IF EXISTS message_citations")
    op.execute("DROP TABLE IF EXISTS chat_messages")
    op.execute("DROP TABLE IF EXISTS chat_sessions")
    op.execute("DROP TABLE IF EXISTS chunk_embeddings")
    op.execute("DROP TABLE IF EXISTS document_chunks")
    op.execute("DROP TABLE IF EXISTS documents")
    op.execute("DROP TABLE IF EXISTS collections")
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP EXTENSION IF EXISTS vector")
