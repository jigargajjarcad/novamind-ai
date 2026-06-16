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


# --- SSE event payload schemas (for documentation; not used in route signatures) ---

class CitationPayload(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int | None
    content: str
    relevance_score: float
    citation_index: int | None  # [N] reference found in the response, or None if implicit


class DonePayload(BaseModel):
    message_id: str
    full_content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
