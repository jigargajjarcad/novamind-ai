import uuid

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user_id
from src.db.database import get_db

logger = structlog.get_logger()
router = APIRouter()


@router.get("/usage")
async def get_usage(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Aggregated token usage and cost per user.
    Week 4: Full admin dashboard queries implemented here.
    """
    logger.debug("admin.usage.request", user_id=str(user_id))
    return {"status": "admin panel implemented in Week 4"}


@router.get("/queries")
async def get_query_log(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Query log with latency, token counts, and cost per query.
    Week 4: Full query log with pagination implemented here.
    """
    logger.debug("admin.queries.request", user_id=str(user_id))
    return {"status": "query log implemented in Week 4"}
