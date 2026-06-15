import uuid
from typing import AsyncIterator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class RAGService:
    """
    Week 3: Full RAG query pipeline.
    embed_query → vector_search → rerank → build_prompt → stream_answer → log
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def query(
        self,
        collection_id: uuid.UUID,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        message_history: list[dict],
    ) -> AsyncIterator[dict]:
        # Week 3 implementation:
        # 1. Embed query with AnthropicService
        # 2. Cosine similarity search via pgvector
        # 3. Rerank top 10 → keep top 5
        # 4. Build prompt with context + history
        # 5. Stream Claude response via SSE
        # 6. Extract citations
        # 7. Write to query_logs
        raise NotImplementedError("RAG pipeline implemented in Week 3")
