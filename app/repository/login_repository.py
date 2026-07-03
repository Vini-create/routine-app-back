from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update

from app.models.auth import ExternalIdentity, LoginChallenge, User


async def create_login_challenge(
    session,
    challenge: LoginChallenge,
    *,
    replace_user_challenges: bool = False,
) -> LoginChallenge:
    if replace_user_challenges and challenge.user_id:
        await session.execute(
            update(LoginChallenge)
            .where(
                LoginChallenge.user_id == challenge.user_id,
                LoginChallenge.challenge_type == challenge.challenge_type,
                LoginChallenge.used_at.is_(None),
            )
            .values(used_at=datetime.now(timezone.utc))
        )
    session.add(challenge)
    await session.commit()
    await session.refresh(challenge)
    return challenge


async def get_active_login_challenge(
    session,
    challenge_id: UUID,
    challenge_type: str,
) -> LoginChallenge | None:
    result = await session.execute(
        select(LoginChallenge)
        .where(
            LoginChallenge.id == challenge_id,
            LoginChallenge.challenge_type == challenge_type,
            LoginChallenge.expires_at > datetime.now(timezone.utc),
            LoginChallenge.used_at.is_(None),
        )
        .with_for_update()
    )
    return result.scalar_one_or_none()


async def reject_login_challenge(
    session, challenge: LoginChallenge, max_attempts: int
) -> None:
    challenge.attempts += 1
    if challenge.attempts >= max_attempts:
        challenge.used_at = datetime.now(timezone.utc)
    session.add(challenge)
    await session.commit()


async def consume_login_challenge(session, challenge: LoginChallenge) -> None:
    challenge.used_at = datetime.now(timezone.utc)
    session.add(challenge)
    await session.commit()


async def get_external_identity(
    session,
    provider: str,
    subject: str,
) -> ExternalIdentity | None:
    result = await session.execute(
        select(ExternalIdentity).where(
            ExternalIdentity.provider == provider,
            ExternalIdentity.subject == subject,
        )
    )
    return result.scalar_one_or_none()


async def get_user_for_external_identity(
    session,
    provider: str,
    subject: str,
) -> User | None:
    result = await session.execute(
        select(User)
        .join(ExternalIdentity, ExternalIdentity.user_id == User.id)
        .where(
            ExternalIdentity.provider == provider,
            ExternalIdentity.subject == subject,
        )
    )
    return result.scalar_one_or_none()
