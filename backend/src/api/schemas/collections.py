import uuid
from datetime import datetime

from pydantic import BaseModel


class CreateCollectionRequest(BaseModel):
    name: str
    description: str | None = None


class UpdateCollectionRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class CollectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
