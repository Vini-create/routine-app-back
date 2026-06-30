from datetime import datetime, timezone

from app.models.auth import AuthActionToken
from app.models.auth import User, RefreshToken, UserCredential
from sqlalchemy import select, update
from app.schemas.auth_schemas import AuthActionTokenType
from app.core.security import hash_password

async def get_user_by_email(session, email: str) -> User | None:
    result =await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session, user_id: str) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(session, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def update_user(session, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def delete_user(session, user: User) -> None:
    await session.delete(user)
    await session.commit()

async def store_refresh_token(session, token: RefreshToken) -> RefreshToken:
    session.add(token)
    await session.commit()
    return token

async def create_user_credentials(session, credential: UserCredential) -> UserCredential:
    session.add(credential)
    await session.commit()
    await session.refresh(credential)
    return credential


async def get_refresh_token_by_hash(session, token_hash: str) -> RefreshToken | None:
    result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    return result.scalar_one_or_none()      


async def revoke_refresh_token_for_user(
    session,
    user_id: str,
    token_hash: str,
) -> None:
    # Scoping by user prevents a valid session from revoking another user's token.
    await session.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.token_hash == token_hash,
        )
        .values(revoked=True)
    )
    await session.commit()


async def deactivate_user_and_revoke_tokens(session, user: User) -> User:
    # Keep related data under the existing soft-deletion strategy, but make every
    # access and refresh token unusable immediately.
    now = datetime.now(timezone.utc)
    user.is_active = False
    user.pending_deletion = True
    user.deleted_at = now
    session.add(user)
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .values(revoked=True)
    )
    await session.commit()
    await session.refresh(user)
    return user

async def get_user_credentials_by_user_id(session, user_id: str) -> UserCredential | None:
    result = await session.execute(select(UserCredential).where(UserCredential.user_id == user_id))
    return result.scalar_one_or_none()

async def store_auth_action_token(session, user_id: str, token_type: AuthActionTokenType, token_hash: str, expires_at: datetime) -> AuthActionToken:

    auth_action_token = AuthActionToken(
        user_id=user_id,
        token_hash=token_hash,
        token_type=token_type,
        expires_at=expires_at
    )

    session.add(auth_action_token)
    await session.commit()
    await session.refresh(auth_action_token)

    return auth_action_token

async def delete_auth_action_token(session, token_hash: str, token_type: AuthActionTokenType) -> None:
    result = await session.execute(
        select(AuthActionToken).where(
            AuthActionToken.token_hash == token_hash,
            AuthActionToken.token_type == token_type
        )
    )
    auth_action_token = result.scalar_one_or_none()
    if auth_action_token:
        await session.delete(auth_action_token)
        await session.commit()

async def set_user_verified(session, user: User) -> User:
    user.is_verified = True
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

#verify email:
async def verify_and_consume_auth_action_token(session, token_hash: str, token_type: AuthActionTokenType) -> AuthActionToken | None:
    result = await session.execute(
        select(AuthActionToken).where(
            AuthActionToken.token_hash == token_hash,
            AuthActionToken.token_type == token_type,
            AuthActionToken.expires_at > datetime.now(timezone.utc),
            AuthActionToken.used_at.is_(None)
        )
    )
    auth_action_token = result.scalar_one_or_none()
    if auth_action_token:
        auth_action_token.used_at = datetime.now(timezone.utc)
        session.add(auth_action_token)
        await session.commit()
        return auth_action_token
    return None

#forgot password:
async def verify_and_set_new_password(session, token_hash: str, new_password: str) -> bool:
    result = await session.execute(
        select(AuthActionToken).where(
            AuthActionToken.token_hash == token_hash,
            AuthActionToken.token_type == AuthActionTokenType.PASSWORD_RESET,
            AuthActionToken.expires_at > datetime.now(timezone.utc),
            AuthActionToken.used_at.is_(None)
        )
    )
    auth_action_token = result.scalar_one_or_none()
    if auth_action_token:
        user_id = auth_action_token.user_id
        credential = await get_user_credentials_by_user_id(session, user_id)
        if credential:
            credential.password_hash = hash_password(new_password)
            session.add(credential)
            await session.commit()
            auth_action_token.used_at = datetime.now(timezone.utc)
            session.add(auth_action_token)
            await session.commit()
            return True
    return False
