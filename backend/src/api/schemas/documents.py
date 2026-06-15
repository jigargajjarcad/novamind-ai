import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    filename: str
    status: str
    file_size_bytes: int | None
    page_count: int | None
    uploaded_at: datetime
    processed_at: datetime | None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class DocumentDetailResponse(DocumentResponse):
    chunk_count: int = 0
