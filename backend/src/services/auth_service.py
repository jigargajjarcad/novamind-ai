import secrets
import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    ProfileResponse,
    ProfileStatsResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    UpdatePasswordRequest,
    UpdateProfileRequest,
    UserResponse,
)
from src.core.exceptions import (
    EmailAlreadyExistsError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidPasswordError,
    RateLimitError,
    TokenExpiredError,
    TokenInvalidError,
    UserNotFoundError,
)
from src.core.security import create_access_token, hash_password, verify_password
from src.db.repositories.chat_repository import ChatRepository
from src.db.repositories.user_repository import UserRepository
from src.services import email_service

logger = structlog.get_logger()

_VERIFICATION_TTL_HOURS = 24
_RESEND_COOLDOWN_SECONDS = 60
_PASSWORD_RESET_TTL_HOURS = 1


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.chat_repo = ChatRepository(db)

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError(f"Email {data.email} is already registered")

        user = await self.user_repo.create(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
        )

        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=_VERIFICATION_TTL_HOURS)
        await self.user_repo.save(user)

        await email_service.send_verification_email(user.email, user.full_name, token)
        logger.info("auth.register.success", user_id=str(user.id), email=user.email)

        return RegisterResponse(user=UserResponse.model_validate(user))

    async def login(self, data: LoginRequest) -> LoginResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning("auth.login.failed", email=data.email)
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_verified:
            logger.warning("auth.login.unverified", user_id=str(user.id))
            raise EmailNotVerifiedError("Please verify your email before signing in")

        jwt, expires_at = create_access_token(user.id)
        logger.info("auth.login.success", user_id=str(user.id))
        return LoginResponse(token=jwt, expires_at=expires_at)

    async def verify_email(self, token: str) -> LoginResponse:
        user = await self.user_repo.get_by_verification_token(token)
        if not user:
            raise TokenInvalidError("Verification token is invalid")

        now = datetime.now(timezone.utc)
        if not user.verification_token_expires_at or user.verification_token_expires_at < now:
            raise TokenExpiredError("Verification token has expired. Request a new one.")

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None
        await self.user_repo.save(user)

        jwt, expires_at = create_access_token(user.id)
        logger.info("auth.verify_email.success", user_id=str(user.id))
        return LoginResponse(token=jwt, expires_at=expires_at)

    async def resend_verification(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if not user or user.is_verified:
            return

        if user.verification_token_expires_at:
            sent_at = user.verification_token_expires_at - timedelta(hours=_VERIFICATION_TTL_HOURS)
            elapsed = (datetime.now(timezone.utc) - sent_at).total_seconds()
            if elapsed < _RESEND_COOLDOWN_SECONDS:
                raise RateLimitError("Please wait before requesting another verification email")

        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=_VERIFICATION_TTL_HOURS)
        await self.user_repo.save(user)

        await email_service.send_verification_email(user.email, user.full_name, token)
        logger.info("auth.resend_verification.success", user_id=str(user.id))

    async def get_current_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        return UserResponse.model_validate(user)

    async def get_profile(self, user_id: uuid.UUID) -> ProfileResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        total_queries = await self.chat_repo.get_query_count_for_user(user_id)
        return ProfileResponse(
            user=UserResponse.model_validate(user),
            stats=ProfileStatsResponse(
                member_since=user.created_at,
                total_queries=total_queries,
            ),
        )

    async def update_profile(self, user_id: uuid.UUID, data: UpdateProfileRequest) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        if data.full_name is not None:
            user.full_name = data.full_name
        await self.user_repo.save(user)
        logger.info("auth.profile.updated", user_id=str(user_id))
        return UserResponse.model_validate(user)

    async def get_my_usage(self, user_id: uuid.UUID) -> dict:
        stats = await self.chat_repo.get_usage_stats_for_user(user_id)
        recent = await self.chat_repo.get_recent_queries_for_user(user_id, limit=10)
        return {
            "total_queries": stats["query_count"],
            "total_input_tokens": stats["total_input_tokens"],
            "total_output_tokens": stats["total_output_tokens"],
            "total_cost_usd": stats["total_cost_usd"],
            "recent_queries": recent,
        }

    async def change_password(self, user_id: uuid.UUID, data: UpdatePasswordRequest) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        if not verify_password(data.current_password, user.password_hash):
            logger.warning("auth.password.change_failed", user_id=str(user_id))
            raise InvalidPasswordError("Current password is incorrect")
        user.password_hash = hash_password(data.new_password)
        await self.user_repo.save(user)
        logger.info("auth.password.changed", user_id=str(user_id))

    async def forgot_password(self, data: ForgotPasswordRequest) -> None:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not user.is_verified:
            # Always return 200 — do not reveal whether the email exists.
            logger.info("auth.forgot_password.noop", email=data.email)
            return

        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=_PASSWORD_RESET_TTL_HOURS)
        await self.user_repo.save(user)

        await email_service.send_password_reset_email(user.email, user.full_name, token)
        logger.info("auth.forgot_password.sent", user_id=str(user.id))

    async def reset_password(self, data: ResetPasswordRequest) -> None:
        user = await self.user_repo.get_by_password_reset_token(data.token)
        if not user:
            raise TokenInvalidError("Password reset token is invalid")

        now = datetime.now(timezone.utc)
        if not user.password_reset_token_expires_at or user.password_reset_token_expires_at < now:
            raise TokenExpiredError("Password reset token has expired. Request a new one.")

        user.password_hash = hash_password(data.new_password)
        user.password_reset_token = None
        user.password_reset_token_expires_at = None
        await self.user_repo.save(user)
        logger.info("auth.reset_password.success", user_id=str(user.id))
