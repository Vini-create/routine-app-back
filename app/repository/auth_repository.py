from datetime import datetime, timezone

from app.models.auth import AuthActionToken
from app.models.auth import User, RefreshToken, UserCredential
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.schemas.auth_schemas import AuthActionTokenType
from app.core.security import hash_password


async def get_user_by_email(session, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session, user_id: str) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user_with_credentials(
    session,
    user: User,
    credential: UserCredential,
) -> tuple[User, UserCredential]:
    """Persist the account and its password as one database transaction."""
    try:
        session.add(user)
        await session.flush()
        credential.user_id = user.id
        session.add(credential)
        await session.commit()
        await session.refresh(user)
        await session.refresh(credential)
        return user, credential
    except IntegrityError as exc:
        await session.rollback()
        raise ValueError("Email already registered") from exc


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


async def get_refresh_token_by_hash(session, token_hash: str) -> RefreshToken | None:
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
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
        update(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True)
    )
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_credentials_by_user_id(
    session, user_id: str
) -> UserCredential | None:
    result = await session.execute(
        select(UserCredential).where(UserCredential.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def store_auth_action_token(
    session,
    user_id: str,
    token_type: AuthActionTokenType,
    token_hash: str,
    expires_at: datetime,
) -> AuthActionToken:
    now = datetime.now(timezone.utc)
    # A newly issued link replaces older links of the same type. This avoids
    # leaving several valid verification/reset links in different inboxes.
    await session.execute(
        update(AuthActionToken)
        .where(
            AuthActionToken.user_id == user_id,
            AuthActionToken.token_type == token_type,
            AuthActionToken.used_at.is_(None),
        )
        .values(used_at=now)
    )

    auth_action_token = AuthActionToken(
        user_id=user_id,
        token_hash=token_hash,
        token_type=token_type,
        expires_at=expires_at,
    )

    session.add(auth_action_token)
    await session.commit()
    await session.refresh(auth_action_token)

    return auth_action_token


async def verify_email_with_token(session, token_hash: str) -> bool:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(AuthActionToken)
        .where(
            AuthActionToken.token_hash == token_hash,
            AuthActionToken.token_type == AuthActionTokenType.EMAIL_VERIFICATION,
            AuthActionToken.expires_at > now,
            AuthActionToken.used_at.is_(None),
        )
        .with_for_update()
    )
    auth_action_token = result.scalar_one_or_none()
    if not auth_action_token:
        return False

    user = await get_user_by_id(session, auth_action_token.user_id)
    if not user or not user.is_active or user.deleted_at is not None:
        return False

    auth_action_token.used_at = now
    user.is_verified = True
    session.add_all([auth_action_token, user])
    await session.commit()
    return True


# forgot password:
async def verify_and_set_new_password(
    session, token_hash: str, new_password: str
) -> bool:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(AuthActionToken)
        .where(
            AuthActionToken.token_hash == token_hash,
            AuthActionToken.token_type == AuthActionTokenType.PASSWORD_RESET,
            AuthActionToken.expires_at > now,
            AuthActionToken.used_at.is_(None),
        )
        .with_for_update()
    )
    auth_action_token = result.scalar_one_or_none()
    if not auth_action_token:
        return False

    credential = await get_user_credentials_by_user_id(
        session, auth_action_token.user_id
    )
    if not credential:
        credential = UserCredential(
            user_id=auth_action_token.user_id,
            password_hash=hash_password(new_password),
        )
    else:
        credential.password_hash = hash_password(new_password)
    user = await get_user_by_id(session, auth_action_token.user_id)
    if not user:
        return False
    user.has_password = True
    auth_action_token.used_at = now
    session.add_all([credential, auth_action_token, user])
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == auth_action_token.user_id)
        .values(revoked=True)
    )
    await session.commit()
    return True


async def change_password_and_revoke_tokens(
    session,
    credential: UserCredential,
    new_password: str,
) -> None:
    credential.password_hash = hash_password(new_password)
    session.add(credential)
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == credential.user_id)
        .values(revoked=True)
    )
    await session.commit()
