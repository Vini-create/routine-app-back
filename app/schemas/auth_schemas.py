from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from enum import Enum

class Languages(str, Enum):
    ENGLISH_US = "english_us"
    PORTUGUESE_BR = "portuguese_br"
    FRENCH = "french"
    ESPANISH = "spanish"

class UserCreate(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None
    language: Languages

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str | None = None

class RefreshToken(BaseModel):
    refresh_token: str      