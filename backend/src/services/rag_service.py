import re
import uuid
from typing import Any, AsyncIterator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.repositories.document_repository import ChunkSearchResult, DocumentRepository
from src.services.anthropic_service import AnthropicService

logger = structlog.get_logger()

_SYSTEM_INSTRUCTIONS = (
    "You are a document assistant. "
    "Answer questions using ONLY the context provided below. "
    "Always cite the source document and page number for every claim using [N] notation "
    "(e.g., [1], [2]). "
    "If the answer is not found in the provided context, respond with exactly: "
    "'I couldn't find that in the uploaded documents.'"
)

_CITATION_PATTERN = re.compile(r"\[(\d+)\]")


class RAGService:
    """
    RAG query pipeline: embed → vector search → rerank → prompt → Claude stream → citations.

    Yields event dicts consumed by ChatService:
        {"type": "chunk",  "text": str}
        {"type": "result", "full_content": str, "citations": list[dict], "usage": dict}
    """

    def __init__(self, db: AsyncSession):
        self.doc_repo = DocumentRepository(db)
        self.anthropic = AnthropicService()

    async def query(
        self,
        collection_id: uuid.UUID,
        query_text: str,
        message_history: list[dict],
    ) -> AsyncIterator[dict[str, Any]]:
        return self._run(collection_id, query_text, message_history)

    async def _run(
        self,
        collection_id: uuid.UUID,
        query_text: str,
        message_history: list[dict],
    ) -> AsyncIterator[dict[str, Any]]:
        # 1. Embed the query
        query_vectors = await self.anthropic.embed([query_text], input_type="query")
        query_embedding = query_vectors[0]
        logger.debug("rag.query.embedded", query_len=len(query_text))

        # 2. Cosine similarity search — retrieve top-k candidates
        candidates = await self.doc_repo.search_similar_chunks(
            collection_id=collection_id,
            query_embedding=query_embedding,
            top_k=settings.TOP_K_RETRIEVAL,
        )
        logger.info(
            "rag.retrieval.done",
            collection_id=str(collection_id),
            candidates=len(candidates),
        )

        # 3. Rerank candidates → keep top-k final
        reranked = await self._rerank(query_text, candidates, top_k=settings.TOP_K_RERANK)

        # 4. Build prompt
        system_prompt = self._build_system_prompt(reranked)
        claude_messages = list(message_history) + [{"role": "user", "content": query_text}]

        # 5. Stream Claude response
        full_content = ""
        usage: dict = {}

        async for text, usage_data in self.anthropic.stream_answer(system_prompt, claude_messages):
            if text:
                full_content += text
                yield {"type": "chunk", "text": text}
            if usage_data:
                usage = usage_data

        # 6. Extract which context blocks Claude explicitly cited
        citations = self._build_citations(full_content, reranked)

        logger.info(
            "rag.query.completed",
            chunks_used=len(reranked),
            explicit_citations=sum(1 for c in citations if c["citation_index"] is not None),
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            cost_usd=usage.get("cost_usd"),
        )

        yield {
            "type": "result",
            "full_content": full_content,
            "citations": citations,
            "chunks_retrieved": len(candidates),
            "usage": usage,
        }

    async def _rerank(
        self,
        query_text: str,
        candidates: list[ChunkSearchResult],
        top_k: int,
    ) -> list[ChunkSearchResult]:
        """Rerank candidates using the Voyage AI reranker, return top_k ordered by relevance."""
        if not candidates:
            return []

        documents = [c.content for c in candidates]
        ranked_indices = await self.anthropic.rerank(query_text, documents, top_k=top_k)

        return [candidates[idx] for idx, _ in ranked_indices]

    def _build_system_prompt(self, chunks: list[ChunkSearchResult]) -> str:
        """
        Build the system prompt with numbered context blocks.
        Format mirrors the PRD template: [N] Document: filename | Page: N\n"content"
        """
        if not chunks:
            context_section = "No relevant documents were found in this collection."
        else:
            blocks = []
            for i, chunk in enumerate(chunks, start=1):
                page = f"Page: {chunk.page_number}" if chunk.page_number else "Page: unknown"
                blocks.append(
                    f"[{i}] Document: {chunk.filename} | {page}\n\"{chunk.content}\""
                )
            context_section = "\n\n".join(blocks)

        return f"{_SYSTEM_INSTRUCTIONS}\n\nContext:\n{context_section}"

    def _build_citations(
        self,
        full_content: str,
        chunks: list[ChunkSearchResult],
    ) -> list[dict]:
        """
        Map context block references ([1], [2], …) in Claude's response back to chunks.

        All reranked chunks are returned as potential citations. Chunks that Claude
        explicitly referenced get a citation_index; others get citation_index=None.
        """
        # Find all [N] references in the response (deduplicated, order of first appearance)
        seen: set[int] = set()
        explicit_indices: list[int] = []
        for m in _CITATION_PATTERN.finditer(full_content):
            n = int(m.group(1))
            if n not in seen:
                seen.add(n)
                explicit_indices.append(n)

        # Build citation list — 1-indexed context blocks map to 0-indexed chunks
        citations: list[dict] = []
        for i, chunk in enumerate(chunks, start=1):
            citation_index = explicit_indices.index(i) + 1 if i in seen else None
            citations.append(
                {
                    "chunk_id": str(chunk.chunk_id),
                    "document_id": str(chunk.document_id),
                    "filename": chunk.filename,
                    "page_number": chunk.page_number,
                    "content": chunk.content[:500],  # truncated for SSE payload size
                    "relevance_score": round(max(0.0, 1.0 - chunk.distance), 4),
                    "citation_index": citation_index,
                }
            )

        return citations
