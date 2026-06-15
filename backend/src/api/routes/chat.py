import uuid

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.chat import (
    CreateSessionRequest,
    SendMessageRequest,
    SessionResponse,
    SessionWithMessagesResponse,
)
from src.core.security import get_current_user_id
from src.db.database import get_db
from src.services.chat_service import ChatService

logger = structlog.get_logger()
router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: CreateSessionRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("chat.session.create.request", user_id=str(user_id), collection_id=str(body.collection_id))
    service = ChatService(db)
    return await service.create_session(user_id, body)


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("chat.sessions.list.request", user_id=str(user_id))
    service = ChatService(db)
    return await service.list_sessions(user_id)


@router.get("/sessions/{session_id}", response_model=SessionWithMessagesResponse)
async def get_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("chat.session.get.request", session_id=str(session_id), user_id=str(user_id))
    service = ChatService(db)
    return await service.get_session(session_id, user_id)


@router.post("/sessions/{session_id}/messages", status_code=status.HTTP_202_ACCEPTED)
async def send_message(
    session_id: uuid.UUID,
    body: SendMessageRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a Server-Sent Events stream with chunk, citations, and done events.
    Week 3: Full RAG pipeline and SSE streaming implemented here.
    """
    logger.debug("chat.message.send.request", session_id=str(session_id), user_id=str(user_id))
    # Week 3: return EventSourceResponse with RAG pipeline stream
    return {"status": "streaming not yet implemented — Week 3"}


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("chat.session.delete.request", session_id=str(session_id), user_id=str(user_id))
    service = ChatService(db)
    await service.delete_session(session_id, user_id)
