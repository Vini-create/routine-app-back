from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Optional
from uuid import UUID
from enum import Enum


class Languages(str, Enum):
    ENGLISH_US = "english_us"
    PORTUGUESE_BR = "portuguese_br"
    FRENCH = "french"
    ESPANISH = "spanish"


class Plans(str, Enum):
    FREE = "free"
    PRO = "pro"
    MAX = "max"


class AuthActionTokenType(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=72)
    display_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    language: Optional[Languages] = Languages.ENGLISH_US


class UserSimpleUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    language: Optional[Languages] = None

    @model_validator(mode="after")
    def reject_null_language(self):
        if "language" in self.model_fields_set and self.language is None:
            raise ValueError("language cannot be null")
        return self


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=72)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginChallengeResponse(BaseModel):
    challenge_id: UUID
    masked_email: str
    expires_at: str


class LoginCodeVerifyRequest(BaseModel):
    challenge_id: UUID
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class LoginCodeResendRequest(BaseModel):
    challenge_id: UUID


class GoogleChallengeResponse(BaseModel):
    challenge_id: UUID
    nonce: str
    expires_at: str


class GoogleLoginRequest(BaseModel):
    challenge_id: UUID
    credential: str = Field(min_length=100, max_length=10_000)
    language: Languages = Languages.ENGLISH_US


class TokenData(BaseModel):
    user_id: UUID | None = None


class RefreshTokenSchema(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=256)


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class UserRegisterResponse(BaseModel):
    message: str
    user_id: str


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    display_name: Optional[str]
    language: Optional[Languages]
    signature_plan: Optional[Plans]
    is_verified: bool
    has_password: bool


class AuthActionTokenVerify(BaseModel):
    token: str = Field(min_length=20, max_length=256)
    token_type: AuthActionTokenType


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=255)


class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(max_length=255)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=256)
    new_password: str = Field(min_length=8, max_length=72)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=8, max_length=72)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=20, max_length=256)


class MessageResponse(BaseModel):
    message: str
