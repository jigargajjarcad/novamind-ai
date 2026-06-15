import uuid

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.collections import CollectionResponse, CreateCollectionRequest, UpdateCollectionRequest
from src.core.security import get_current_user_id
from src.db.database import get_db
from src.services.collection_service import CollectionService

logger = structlog.get_logger()
router = APIRouter()


@router.get("", response_model=list[CollectionResponse])
async def list_collections(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("collections.list.request", user_id=str(user_id))
    service = CollectionService(db)
    return await service.list_for_user(user_id)


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    body: CreateCollectionRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("collections.create.request", user_id=str(user_id), name=body.name)
    service = CollectionService(db)
    return await service.create(user_id, body)


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("collections.get.request", collection_id=str(collection_id), user_id=str(user_id))
    service = CollectionService(db)
    return await service.get(collection_id, user_id)


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: uuid.UUID,
    body: UpdateCollectionRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("collections.update.request", collection_id=str(collection_id), user_id=str(user_id))
    service = CollectionService(db)
    return await service.update(collection_id, user_id, body)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("collections.delete.request", collection_id=str(collection_id), user_id=str(user_id))
    service = CollectionService(db)
    await service.delete(collection_id, user_id)
