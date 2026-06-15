import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.collections import (
    CollectionResponse,
    CreateCollectionRequest,
    UpdateCollectionRequest,
)
from src.core.exceptions import CollectionNotFoundError, ForbiddenError
from src.db.repositories.collection_repository import CollectionRepository

logger = structlog.get_logger()


class CollectionService:
    def __init__(self, db: AsyncSession):
        self.repo = CollectionRepository(db)

    async def list_for_user(self, user_id: uuid.UUID) -> list[CollectionResponse]:
        collections = await self.repo.get_all_for_user(user_id)
        return [CollectionResponse.model_validate(c) for c in collections]

    async def get(self, collection_id: uuid.UUID, user_id: uuid.UUID) -> CollectionResponse:
        collection = await self.repo.get_by_id_for_user(collection_id, user_id)
        if not collection:
            raise CollectionNotFoundError(f"Collection {collection_id} not found")
        return CollectionResponse.model_validate(collection)

    async def create(self, user_id: uuid.UUID, data: CreateCollectionRequest) -> CollectionResponse:
        collection = await self.repo.create(
            user_id=user_id,
            name=data.name,
            description=data.description,
        )
        logger.info("collection.created", collection_id=str(collection.id), user_id=str(user_id))
        return CollectionResponse.model_validate(collection)

    async def update(self, collection_id: uuid.UUID, user_id: uuid.UUID, data: UpdateCollectionRequest) -> CollectionResponse:
        collection = await self.repo.get_by_id(collection_id)
        if not collection:
            raise CollectionNotFoundError(f"Collection {collection_id} not found")
        if collection.user_id != user_id:
            raise ForbiddenError("You do not have access to this collection")

        updated = await self.repo.update(collection, name=data.name, description=data.description)
        logger.info("collection.updated", collection_id=str(collection_id), user_id=str(user_id))
        return CollectionResponse.model_validate(updated)

    async def delete(self, collection_id: uuid.UUID, user_id: uuid.UUID) -> None:
        collection = await self.repo.get_by_id(collection_id)
        if not collection:
            raise CollectionNotFoundError(f"Collection {collection_id} not found")
        if collection.user_id != user_id:
            raise ForbiddenError("You do not have access to this collection")

        await self.repo.delete(collection)
        logger.info("collection.deleted", collection_id=str(collection_id), user_id=str(user_id))
