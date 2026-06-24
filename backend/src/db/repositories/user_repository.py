import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.verification_token == token)
        )
        return result.scalar_one_or_none()

    async def get_by_password_reset_token(self, token: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.password_reset_token == token)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str, full_name: str | None = None) -> User:
        user = User(email=email, password_hash=password_hash, full_name=full_name)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def save(self, user: User) -> User:
        """Commit in-place mutations to an already-tracked User and return it."""
        await self.db.commit()
        await self.db.refresh(user)
        return user
