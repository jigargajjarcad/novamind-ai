import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.chat import ChatMessage, ChatSession, MessageCitation, QueryLog


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: uuid.UUID, collection_id: uuid.UUID, name: str | None = None) -> ChatSession:
        session = ChatSession(user_id=user_id, collection_id=collection_id, name=name)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session_by_id(self, session_id: uuid.UUID) -> ChatSession | None:
        result = await self.db.execute(select(ChatSession).where(ChatSession.id == session_id))
        return result.scalar_one_or_none()

    async def get_session_for_user(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_sessions_for_user(self, user_id: uuid.UUID) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_session_with_messages(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_recent_messages(self, session_id: uuid.UUID, limit: int = 6) -> list[ChatMessage]:
        """Returns up to `limit` most recent messages in chronological order (oldest first)."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))

    async def create_message(self, session_id: uuid.UUID, role: str, content: str) -> ChatMessage:
        message = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def create_citations(self, citations: list[MessageCitation]) -> list[MessageCitation]:
        self.db.add_all(citations)
        await self.db.commit()
        return citations

    async def create_query_log(self, log: QueryLog) -> QueryLog:
        self.db.add(log)
        await self.db.commit()
        return log

    async def delete_session(self, session: ChatSession) -> None:
        await self.db.delete(session)
        await self.db.commit()

    async def get_usage_by_user(self) -> list[dict]:
        result = await self.db.execute(
            select(
                QueryLog.user_id,
                QueryLog.input_tokens,
                QueryLog.output_tokens,
                QueryLog.cost_usd,
            )
        )
        return [dict(row._mapping) for row in result.all()]
