from typing import AsyncIterator

import structlog
import anthropic
import voyageai

from src.core.config import settings

logger = structlog.get_logger()

CHAT_MODEL = "claude-sonnet-4-6"
EMBEDDING_MODEL = "voyage-3"
RERANK_MODEL = "rerank-2-lite"
EMBEDDING_DIM = 1024

# claude-sonnet-4-6 pricing
CHAT_INPUT_TOKEN_COST = 0.000003   # $3 per 1M input tokens
CHAT_OUTPUT_TOKEN_COST = 0.000015  # $15 per 1M output tokens

# voyage-3 pricing: $0.06 per 1M tokens
EMBEDDING_TOKEN_COST = 0.00000006


class AnthropicService:
    """Single wrapper for all Anthropic/Voyage API calls. Tracks tokens and cost on every call."""

    def __init__(self):
        self.chat_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.embed_client = voyageai.AsyncClient(api_key=settings.VOYAGE_API_KEY)

    async def embed(self, texts: list[str], input_type: str = "document") -> list[list[float]]:
        """
        Generate embeddings using voyage-3 (1024 dimensions).

        input_type: "document" for indexed content, "query" for search-time queries.
        Batches internally to stay within Voyage AI's 128-item batch limit.
        """
        if not texts:
            return []

        all_embeddings: list[list[float]] = []
        total_tokens = 0
        batch_size = 64  # safe margin below the 128-item API limit

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            result = await self.embed_client.embed(
                batch,
                model=EMBEDDING_MODEL,
                input_type=input_type,
            )
            all_embeddings.extend(result.embeddings)
            total_tokens += result.total_tokens

        cost_usd = total_tokens * EMBEDDING_TOKEN_COST
        logger.info(
            "voyage.embed.completed",
            model=EMBEDDING_MODEL,
            text_count=len(texts),
            total_tokens=total_tokens,
            cost_usd=round(cost_usd, 6),
        )

        return all_embeddings

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 5,
    ) -> list[tuple[int, float]]:
        """
        Rerank documents against a query using Voyage AI reranker.

        Returns (original_index, relevance_score) pairs sorted by descending score.
        Falls back to identity ordering (highest cosine similarity first) on failure.
        """
        if not documents:
            return []

        effective_top_k = min(top_k, len(documents))

        try:
            result = await self.embed_client.rerank(
                query=query,
                documents=documents,
                model=RERANK_MODEL,
                top_k=effective_top_k,
            )
            ranked = [(r.index, float(r.relevance_score)) for r in result.results]
            logger.info(
                "voyage.rerank.completed",
                model=RERANK_MODEL,
                input_count=len(documents),
                output_count=len(ranked),
            )
            return ranked

        except Exception as e:
            logger.warning("voyage.rerank.failed_falling_back", error=str(e))
            # Fallback: keep top_k in original order (already sorted by cosine distance)
            return [(i, 1.0) for i in range(effective_top_k)]

    async def stream_answer(
        self,
        system_prompt: str,
        messages: list[dict],
    ) -> AsyncIterator[tuple[str, dict | None]]:
        """
        Stream a Claude completion. Yields (text_chunk, usage_dict).
        usage_dict is only non-None on the final yield and contains token counts + cost.
        """
        async with self.chat_client.messages.stream(
            model=CHAT_MODEL,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text, None

            final = await stream.get_final_message()
            usage = {
                "input_tokens": final.usage.input_tokens,
                "output_tokens": final.usage.output_tokens,
                "cost_usd": (
                    final.usage.input_tokens * CHAT_INPUT_TOKEN_COST
                    + final.usage.output_tokens * CHAT_OUTPUT_TOKEN_COST
                ),
            }
            yield "", usage

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (
            input_tokens * CHAT_INPUT_TOKEN_COST
            + output_tokens * CHAT_OUTPUT_TOKEN_COST
        )
