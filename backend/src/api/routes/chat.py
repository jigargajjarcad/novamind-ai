import uuid

import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
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


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: uuid.UUID,
    body: SendMessageRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream a RAG-grounded response as Server-Sent Events.

    Event types:
      chunk      — incremental text from Claude: {"text": "..."}
      citations  — retrieved context blocks after streaming completes
      done       — final summary: message_id, token counts, cost, latency
      error      — on failure: {"code": "...", "message": "..."}
    """
    logger.debug(
        "chat.message.send.request",
        session_id=str(session_id),
        user_id=str(user_id),
        content_len=len(body.content),
    )
    service = ChatService(db)
    event_stream = await service.stream_message(session_id, user_id, body.content)

    return StreamingResponse(
        event_stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx response buffering
            "Connection": "keep-alive",
        },
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("chat.session.delete.request", session_id=str(session_id), user_id=str(user_id))
    service = ChatService(db)
    await service.delete_session(session_id, user_id)
