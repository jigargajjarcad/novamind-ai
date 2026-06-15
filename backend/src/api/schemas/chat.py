import uuid
from datetime import datetime

from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    collection_id: uuid.UUID
    name: str | None = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID | None
    name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionWithMessagesResponse(SessionResponse):
    messages: list[MessageResponse] = []


class SendMessageRequest(BaseModel):
    content: str
