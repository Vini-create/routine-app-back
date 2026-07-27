from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key_value,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def create_refresh_token() -> str:
    random_string = secrets.token_urlsafe(32)
    token_data = random_string
    return token_data


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def hash_login_secret(challenge_id: str, secret: str) -> str:
    value = f"{challenge_id}:{secret}".encode()
    return hmac.new(
        settings.secret_key_value.encode(),
        value,
        hashlib.sha256,
    ).hexdigest()


def verify_login_secret(challenge_id: str, secret: str, expected_hash: str) -> bool:
    return hmac.compare_digest(
        hash_login_secret(challenge_id, secret),
        expected_hash,
    )


def create_numeric_code(length: int = 6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def get_user_id_from_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key_value,
            algorithms=[settings.algorithm],
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None:
            raise ValueError("Invalid token")
        if token_type != expected_type:
            raise ValueError("Invalid token")
        return user_id
    except JWTError:
        raise ValueError("Invalid token")


def create_random_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)
