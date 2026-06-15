import uuid
from typing import AsyncIterator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.chat import CreateSessionRequest, MessageResponse, SessionResponse, SessionWithMessagesResponse
from src.core.exceptions import ChatSessionNotFoundError, CollectionNotFoundError
from src.db.repositories.chat_repository import ChatRepository
from src.db.repositories.collection_repository import CollectionRepository

logger = structlog.get_logger()


class ChatService:
    def __init__(self, db: AsyncSession):
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
        # Week 3: Full RAG pipeline with Claude streaming will be implemented here.
        # Requires: ingestion_service, rag_service, anthropic_service.
        raise NotImplementedError("Streaming chat implemented in Week 3")
