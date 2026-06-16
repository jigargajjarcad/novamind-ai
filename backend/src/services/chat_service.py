import json
import time
import uuid
from typing import AsyncIterator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.chat import CreateSessionRequest, SessionResponse, SessionWithMessagesResponse
from src.core.exceptions import ChatSessionNotFoundError, CollectionNotFoundError
from src.db.repositories.chat_repository import ChatRepository
from src.db.repositories.collection_repository import CollectionRepository
from src.models.chat import MessageCitation, QueryLog
from src.services.rag_service import RAGService

logger = structlog.get_logger()


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.col_repo = CollectionRepository(db)

    async def create_session(self, user_id: uuid.UUID, data: CreateSessionRequest) -> SessionResponse:
        collection = await self.col_repo.get_by_id_for_user(data.collection_id, user_id)
        if not collection:
            raise CollectionNotFoundError(f"Collection {data.collection_id} not found")

        session = await self.chat_repo.create_session(
            user_id=user_id,
            collection_id=data.collection_id,
            name=data.name,
        )
        logger.info("chat.session.created", session_id=str(session.id), user_id=str(user_id))
        return SessionResponse.model_validate(session)

    async def list_sessions(self, user_id: uuid.UUID) -> list[SessionResponse]:
        sessions = await self.chat_repo.get_sessions_for_user(user_id)
        return [SessionResponse.model_validate(s) for s in sessions]

    async def get_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> SessionWithMessagesResponse:
        session = await self.chat_repo.get_session_with_messages(session_id, user_id)
        if not session:
            raise ChatSessionNotFoundError(f"Chat session {session_id} not found")
        return SessionWithMessagesResponse.model_validate(session)

    async def delete_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> None:
        session = await self.chat_repo.get_session_for_user(session_id, user_id)
        if not session:
            raise ChatSessionNotFoundError(f"Chat session {session_id} not found")

        await self.chat_repo.delete_session(session)
        logger.info("chat.session.deleted", session_id=str(session_id), user_id=str(user_id))

    async def stream_message(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> AsyncIterator[str]:
        """
        Full RAG pipeline as an async generator that yields SSE-formatted strings.

        Event sequence:
            event: chunk       — streaming text from Claude (one per token group)
            event: citations   — all retrieved context blocks with relevance scores
            event: done        — final message_id, token counts, cost, latency
            event: error       — only on fatal failure before/during streaming
        """
        return self._stream(session_id, user_id, content)

    async def _stream(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> AsyncIterator[str]:
        started_at = time.monotonic()

        # --- Validate session ---
        session = await self.chat_repo.get_session_for_user(session_id, user_id)
        if not session:
            yield _sse("error", {"code": "CHAT_SESSION_NOT_FOUND", "message": "Session not found"})
            return

        if not session.collection_id:
            yield _sse("error", {"code": "NO_COLLECTION", "message": "Session has no associated collection"})
            return

        try:
            # --- Fetch conversation history (last 6 messages before this one) ---
            recent_messages = await self.chat_repo.get_recent_messages(session_id, limit=6)
            message_history = [{"role": m.role, "content": m.content} for m in recent_messages]

            # --- Persist user message ---
            user_msg = await self.chat_repo.create_message(session_id, "user", content)
            logger.info(
                "chat.message.user_saved",
                session_id=str(session_id),
                message_id=str(user_msg.id),
            )

            # --- Run RAG pipeline ---
            rag = RAGService(self.db)
            rag_events = await rag.query(
                collection_id=session.collection_id,
                query_text=content,
                message_history=message_history,
            )

            full_content = ""
            rag_result: dict | None = None

            async for event in rag_events:
                if event["type"] == "chunk":
                    full_content += event["text"]
                    yield _sse("chunk", {"text": event["text"]})
                elif event["type"] == "result":
                    rag_result = event

            # --- Persist assistant message ---
            assistant_msg = await self.chat_repo.create_message(session_id, "assistant", full_content)

            # --- Persist citations ---
            citations_data: list[dict] = []
            if rag_result and rag_result.get("citations"):
                citation_models = [
                    MessageCitation(
                        message_id=assistant_msg.id,
                        chunk_id=uuid.UUID(c["chunk_id"]),
                        relevance_score=c["relevance_score"],
                        citation_index=c["citation_index"],
                    )
                    for c in rag_result["citations"]
                ]
                await self.chat_repo.create_citations(citation_models)
                citations_data = rag_result["citations"]

            # --- Log to query_logs ---
            usage = rag_result.get("usage", {}) if rag_result else {}
            latency_ms = int((time.monotonic() - started_at) * 1000)

            await self.chat_repo.create_query_log(
                QueryLog(
                    user_id=user_id,
                    session_id=session_id,
                    query=content,
                    chunks_retrieved=rag_result.get("chunks_retrieved", 0) if rag_result else 0,
                    input_tokens=usage.get("input_tokens"),
                    output_tokens=usage.get("output_tokens"),
                    cost_usd=usage.get("cost_usd"),
                    latency_ms=latency_ms,
                )
            )

            logger.info(
                "chat.message.completed",
                session_id=str(session_id),
                message_id=str(assistant_msg.id),
                latency_ms=latency_ms,
                cost_usd=usage.get("cost_usd"),
            )

            # --- Send final SSE events ---
            yield _sse("citations", citations_data)
            yield _sse(
                "done",
                {
                    "message_id": str(assistant_msg.id),
                    "full_content": full_content,
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "cost_usd": usage.get("cost_usd", 0),
                    "latency_ms": latency_ms,
                },
            )

        except Exception as e:
            logger.error(
                "chat.stream_message.failed",
                session_id=str(session_id),
                error=str(e),
                exc_info=True,
            )
            yield _sse("error", {"code": "INTERNAL_ERROR", "message": "An error occurred during response generation"})


def _sse(event: str, data: object) -> str:
    """Format a single SSE event frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
