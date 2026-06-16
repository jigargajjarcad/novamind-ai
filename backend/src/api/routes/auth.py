import uuid

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    UserResponse,
    VerifyEmailRequest,
)
from src.core.security import get_current_user_id
from src.db.database import get_db
from src.services.auth_service import AuthService

logger = structlog.get_logger()
router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    logger.debug("auth.register.request", email=body.email)
    service = AuthService(db)
    return await service.register(body)


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.debug("auth.login.request", email=body.email)
    service = AuthService(db)
    return await service.login(body)


@router.post("/verify-email", response_model=LoginResponse)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    logger.debug("auth.verify_email.request")
    service = AuthService(db)
    return await service.verify_email(body.token)


@router.post("/resend-verification", status_code=204)
async def resend_verification(body: ResendVerificationRequest, db: AsyncSession = Depends(get_db)):
    logger.debug("auth.resend_verification.request")
    service = AuthService(db)
    await service.resend_verification(body.email)


@router.get("/me", response_model=UserResponse)
async def me(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.get_current_user(user_id)
