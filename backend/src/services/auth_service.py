import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, UserResponse
from src.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError, UserNotFoundError
from src.core.security import create_access_token, hash_password, verify_password
from src.db.repositories.user_repository import UserRepository

logger = structlog.get_logger()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError(f"Email {data.email} is already registered")

        password_hash = hash_password(data.password)
        user = await self.user_repo.create(
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
        )

        token, _ = create_access_token(user.id)
        logger.info("auth.register.success", user_id=str(user.id), email=user.email)

        return RegisterResponse(
            user=UserResponse.model_validate(user),
            token=token,
        )

    async def login(self, data: LoginRequest) -> LoginResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning("auth.login.failed", email=data.email)
            raise InvalidCredentialsError("Invalid email or password")

        token, expires_at = create_access_token(user.id)
        logger.info("auth.login.success", user_id=str(user.id))

        return LoginResponse(token=token, expires_at=expires_at)

    async def get_current_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        return UserResponse.model_validate(user)
