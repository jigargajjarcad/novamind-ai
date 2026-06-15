import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.collection import Collection


class CollectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_for_user(self, user_id: uuid.UUID) -> list[Collection]:
        result = await self.db.execute(
            select(Collection).where(Collection.user_id == user_id).order_by(Collection.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, collection_id: uuid.UUID) -> Collection | None:
        result = await self.db.execute(select(Collection).where(Collection.id == collection_id))
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, collection_id: uuid.UUID, user_id: uuid.UUID) -> Collection | None:
        result = await self.db.execute(
            select(Collection).where(Collection.id == collection_id, Collection.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: uuid.UUID, name: str, description: str | None = None) -> Collection:
        collection = Collection(user_id=user_id, name=name, description=description)
        self.db.add(collection)
        await self.db.commit()
        await self.db.refresh(collection)
        return collection

    async def update(self, collection: Collection, name: str | None = None, description: str | None = None) -> Collection:
        if name is not None:
            collection.name = name
        if description is not None:
            collection.description = description
        await self.db.commit()
        await self.db.refresh(collection)
        return collection

    async def delete(self, collection: Collection) -> None:
        await self.db.delete(collection)
        await self.db.commit()
