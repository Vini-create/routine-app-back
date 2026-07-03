#services de autenticação
from datetime import datetime, timedelta, timezone


from app.core.config import settings

from app.models.auth import RefreshToken, User, UserCredential
from app.repository.auth_repository import (
    create_user,
    create_user_credentials,
    deactivate_user_and_revoke_tokens,
    get_refresh_token_by_hash,
    get_user_by_email,
    get_user_by_id,
    get_user_credentials_by_user_id,
    revoke_refresh_token_for_user,
    set_user_verified,
    store_auth_action_token,
    store_refresh_token,
    update_user,
    verify_and_consume_auth_action_token,
    verify_and_set_new_password,
)
from app.core.security import create_random_token, hash_password, verify_password, create_access_token, create_refresh_token, hash_token
from app.schemas.auth_schemas import AuthActionTokenType, UserSimpleUpdate
from app.services.email_service import send_password_reset_email, send_verification_email

async def register_user(session, email: str, display_name: str, language: str, password: str):
    existing_user = await get_user_by_email(session, email)
    if existing_user:
        raise ValueError("Email already registered")
    
    hashed_password = hash_password(password)
    new_user = await create_user(session,User(email=email, display_name=display_name, language=language))
    new_user_credentials = await create_user_credentials(session,UserCredential(user_id=new_user.id, password_hash=hashed_password))
    return new_user, new_user_credentials

async def authenticate_user(session, email: str, password: str):
    user = await get_user_by_email(session, email)
    if not user:
        raise ValueError("Invalid credentials")
    if not user.is_active or user.deleted_at is not None:
        raise ValueError("Invalid credentials")
    if not user.is_verified:
        raise ValueError("Email not verified")
    credentials = await get_user_credentials_by_user_id(session, user.id) 
    if not credentials or not verify_password(password, credentials.password_hash):
        raise ValueError("Invalid credentials")
    return user

async def create_tokens_for_user(session, user: User):
    access_token = create_access_token(data={"sub": str(user.id), "type": "access"})
    refresh_token = create_refresh_token()
    refresh_token_hash = hash_token(refresh_token)
    refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    await store_refresh_token(session, RefreshToken(user_id=user.id, token_hash=refresh_token_hash, expires_at=refresh_token_expires_at))
    
    return access_token, refresh_token

async def refresh_access_token(session, refresh_token: str):
    refresh_token_hash = hash_token(refresh_token)
    stored_refresh_token = await get_refresh_token_by_hash(session, refresh_token_hash)
    
    if (
        not stored_refresh_token
        or stored_refresh_token.revoked
        or stored_refresh_token.expires_at < datetime.now(timezone.utc)
    ):
        raise ValueError("Invalid or expired refresh token")
    
    user = await get_user_by_id(session, stored_refresh_token.user_id)
    if not user:
        raise ValueError("User not found")
    if not user.is_active or user.deleted_at is not None or not user.is_verified:
        raise ValueError("User not allowed")
    
    return create_access_token(data={"sub": str(user.id), "type": "access"})


async def update_current_user(session, user: User, payload: UserSimpleUpdate) -> User:
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(user, field, value.value if hasattr(value, "value") else value)
    return await update_user(session, user)


async def logout_session(session, user_id: str, refresh_token: str) -> None:
    await revoke_refresh_token_for_user(session, user_id, hash_token(refresh_token))


async def deactivate_current_user(session, user: User) -> None:
    await deactivate_user_and_revoke_tokens(session, user)

#when user requests password reset or email verification, we create an auth action token and store it in the database. When the user clicks the link in the email, we verify the token and perform the corresponding action (set user as verified or reset password):
async def create_auth_action_token(session, user_id: str, token_type: AuthActionTokenType, expires_in_minutes: int = 30) -> str:
    token = create_random_token()
    token_hash = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    
    await store_auth_action_token(session, user_id=user_id, token_type=token_type, token_hash=token_hash, expires_at=expires_at)
    
    return token

#verify email:
async def verify_user(session, token: str) -> bool:
    token_hash = hash_token(token)
    auth_action_token = await verify_and_consume_auth_action_token(session,token_hash,AuthActionTokenType.EMAIL_VERIFICATION)
    if not auth_action_token:
        return False
    user = await get_user_by_id(session, auth_action_token.user_id)
    if not user:
        return False
    if user.is_verified:
        return True
    await set_user_verified(session, user)
    return True

#forgot password:
async def reset_password(session, token: str, new_password: str) -> bool:
    token_hash = hash_token(token)
    result = await verify_and_set_new_password(session, token_hash, new_password)
    if result:
        return True
    return False

async def request_password_reset(session, email: str) -> None:
    user = await get_user_by_email(session, email)

    if not user:
        return

    token = await create_auth_action_token(session,user_id=str(user.id),token_type=AuthActionTokenType.PASSWORD_RESET,expires_in_minutes=30)
    await send_password_reset_email(user.email, token)


async def request_email_verification(session, email: str) -> None:
    user = await get_user_by_email(session, email)

    # Keep the response generic so the endpoint cannot be used to enumerate accounts.
    if not user or user.is_verified or not user.is_active or user.deleted_at is not None:
        return

    token = await create_auth_action_token(
        session,
        user_id=str(user.id),
        token_type=AuthActionTokenType.EMAIL_VERIFICATION,
        expires_in_minutes=1440,
    )
    await send_verification_email(user.email, token)
