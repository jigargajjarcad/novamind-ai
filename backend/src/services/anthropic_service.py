from typing import AsyncIterator

import structlog
import anthropic

from src.core.config import settings

logger = structlog.get_logger()

EMBEDDING_MODEL = "voyage-3"
CHAT_MODEL = "claude-sonnet-4-6"
INPUT_TOKEN_COST = 0.000003   # $3 per 1M input tokens
OUTPUT_TOKEN_COST = 0.000015  # $15 per 1M output tokens


class AnthropicService:
    """Single wrapper for all Anthropic API calls. Tracks tokens and cost on every call."""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of text chunks."""
        # Week 2: Anthropic does not yet offer a direct embedding API.
        # We will use the voyage-3 model via the anthropic client or
        # voyageai SDK. Placeholder for Week 2 implementation.
        raise NotImplementedError("Embedding generation implemented in Week 2")

    async def stream_answer(
        self,
        system_prompt: str,
        messages: list[dict],
    ) -> AsyncIterator[tuple[str, dict | None]]:
        """
        Stream a Claude completion. Yields (text_chunk, usage_dict).
        usage_dict is only non-None on the final chunk.
        """
        usage = None
        async with self.client.messages.stream(
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
                    final.usage.input_tokens * INPUT_TOKEN_COST
                    + final.usage.output_tokens * OUTPUT_TOKEN_COST
                ),
            }
            yield "", usage

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return input_tokens * INPUT_TOKEN_COST + output_tokens * OUTPUT_TOKEN_COST
