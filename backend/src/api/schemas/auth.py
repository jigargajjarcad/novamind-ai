import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None
    is_admin: bool = False

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    user: UserResponse
    message: str = "Verification email sent. Please check your inbox."


class LoginResponse(BaseModel):
    token: str
    expires_at: datetime


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None


class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class ProfileStatsResponse(BaseModel):
    member_since: datetime
    total_queries: int


class ProfileResponse(BaseModel):
    user: UserResponse
    stats: ProfileStatsResponse
