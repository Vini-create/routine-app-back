from pydantic import BaseModel, EmailStr, Field
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
    language: Optional[Languages] = Languages.ENGLISH_US

class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=72)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    

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
    id: UUID
    email: EmailStr
    display_name: Optional[str]
    language: Optional[Languages]
    signature_plan: Optional[Plans]
    is_verified: bool  

class AuthActionTokenVerify(BaseModel):
    token: str = Field(min_length=20, max_length=256)
    token_type: AuthActionTokenType

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=255)

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=256)
    new_password: str = Field(min_length=8, max_length=72)

class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=20, max_length=256)

class MessageResponse(BaseModel):
    message: str
