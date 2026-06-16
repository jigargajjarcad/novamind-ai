import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.chat import ChatMessage, ChatSession, MessageCitation, QueryLog
from src.models.user import User


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

    async def get_query_count_for_user(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(QueryLog.id)).where(QueryLog.user_id == user_id)
        )
        return result.scalar() or 0

    # --- Admin aggregation queries ---

    async def get_summary_stats(self) -> dict:
        result = await self.db.execute(
            select(
                func.count(QueryLog.id).label("total_queries"),
                func.coalesce(func.sum(QueryLog.input_tokens), 0).label("total_input_tokens"),
                func.coalesce(func.sum(QueryLog.output_tokens), 0).label("total_output_tokens"),
                func.coalesce(func.sum(QueryLog.cost_usd), 0).label("total_cost_usd"),
                func.coalesce(func.avg(QueryLog.latency_ms), 0).label("avg_latency_ms"),
            )
        )
        row = result.one()
        return {
            "total_queries": row.total_queries,
            "total_input_tokens": int(row.total_input_tokens),
            "total_output_tokens": int(row.total_output_tokens),
            "total_cost_usd": float(row.total_cost_usd),
            "avg_latency_ms": float(row.avg_latency_ms),
        }

    async def get_usage_by_user(self) -> list[dict]:
        result = await self.db.execute(
            select(
                User.id.label("user_id"),
                User.email,
                func.count(QueryLog.id).label("query_count"),
                func.coalesce(func.sum(QueryLog.input_tokens), 0).label("total_input_tokens"),
                func.coalesce(func.sum(QueryLog.output_tokens), 0).label("total_output_tokens"),
                func.coalesce(func.sum(QueryLog.cost_usd), 0).label("total_cost_usd"),
            )
            .select_from(QueryLog)
            .join(User, QueryLog.user_id == User.id)
            .group_by(User.id, User.email)
            .order_by(func.sum(QueryLog.cost_usd).desc())
        )
        return [
            {
                "user_id": str(row.user_id),
                "email": row.email,
                "query_count": row.query_count,
                "total_input_tokens": int(row.total_input_tokens),
                "total_output_tokens": int(row.total_output_tokens),
                "total_cost_usd": float(row.total_cost_usd),
            }
            for row in result.all()
        ]

    async def get_recent_query_log(self, limit: int = 50) -> list[dict]:
        result = await self.db.execute(
            select(
                QueryLog.id,
                QueryLog.query,
                QueryLog.chunks_retrieved,
                QueryLog.input_tokens,
                QueryLog.output_tokens,
                QueryLog.cost_usd,
                QueryLog.latency_ms,
                QueryLog.created_at,
                User.email.label("user_email"),
            )
            .select_from(QueryLog)
            .outerjoin(User, QueryLog.user_id == User.id)
            .order_by(QueryLog.created_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": str(row.id),
                "query": row.query[:100] + "…" if len(row.query) > 100 else row.query,
                "user_email": row.user_email,
                "chunks_retrieved": row.chunks_retrieved,
                "input_tokens": row.input_tokens,
                "output_tokens": row.output_tokens,
                "cost_usd": float(row.cost_usd) if row.cost_usd is not None else None,
                "latency_ms": row.latency_ms,
                "created_at": row.created_at.isoformat(),
            }
            for row in result.all()
        ]
