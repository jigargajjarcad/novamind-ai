import uuid

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user_id
from src.db.database import get_db
from src.db.repositories.chat_repository import ChatRepository

logger = structlog.get_logger()
router = APIRouter()


@router.get("/usage")
async def get_usage(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated token usage and cost: summary stats + per-user breakdown."""
    logger.debug("admin.usage.request", user_id=str(user_id))
    repo = ChatRepository(db)
    summary = await repo.get_summary_stats()
    by_user = await repo.get_usage_by_user()
    current_user_id_str = str(user_id)
    my_usage = next((row for row in by_user if row["user_id"] == current_user_id_str), None)
    return {
        "summary": summary,
        "by_user": by_user,
        "current_user_id": current_user_id_str,
        "my_usage": my_usage,
    }


@router.get("/queries")
async def get_query_log(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Recent query log with latency, token counts, and cost."""
    logger.debug("admin.queries.request", user_id=str(user_id))
    repo = ChatRepository(db)
    queries = await repo.get_recent_query_log(limit=50)
    return {"queries": queries}
