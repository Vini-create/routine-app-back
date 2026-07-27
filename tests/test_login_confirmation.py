import pytest
from sqlalchemy import select

from app.billing.models import BillingAccount
from app.core.config import settings
from app.core.security import hash_password
from app.models.auth import ExternalIdentity, User, UserCredential

pytestmark = pytest.mark.asyncio


async def create_verified_user(session, email: str = "member@example.com") -> User:
    user = User(
        email=email,
        display_name="Member",
        language="portuguese_br",
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    await session.flush()
    session.add(
        UserCredential(user_id=user.id, password_hash=hash_password("correct-password"))
    )
    await session.commit()
    await session.refresh(user)
    return user


async def test_password_login_only_issues_tokens_after_one_time_code(
    client, session, monkeypatch
):
    user = await create_verified_user(session)
    delivered_codes: list[str] = []

    async def capture_code(to_email: str, code: str, language: str | None = None):
        assert to_email == user.email
        assert language == "portuguese_br"
        delivered_codes.append(code)

    monkeypatch.setattr("app.services.auth_service.send_login_code_email", capture_code)

    started = await client.post(
        "/auth/login",
        json={"email": user.email, "password": "correct-password"},
    )
    assert started.status_code == 200
    assert "access_token" not in started.json()
    assert started.json()["masked_email"].endswith("@example.com")

    challenge_id = started.json()["challenge_id"]
    wrong = await client.post(
        "/auth/login/verify",
        json={"challenge_id": challenge_id, "code": "000000"},
    )
    assert wrong.status_code == 401

    confirmed = await client.post(
        "/auth/login/verify",
        json={"challenge_id": challenge_id, "code": delivered_codes[-1]},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["access_token"]
    assert confirmed.json()["refresh_token"]

    replay = await client.post(
        "/auth/login/verify",
        json={"challenge_id": challenge_id, "code": delivered_codes[-1]},
    )
    assert replay.status_code == 401


async def test_google_login_creates_verified_account_and_rejects_replay(
    client, session, monkeypatch
):
    monkeypatch.setattr(
        settings, "google_client_id", "test-client.apps.googleusercontent.com"
    )
    challenge = await client.post("/auth/google/challenge")
    assert challenge.status_code == 200

    async def verified_google_credential(_credential: str):
        return {
            "sub": "google-subject-123",
            "email": "google-user@example.com",
            "email_verified": True,
            "name": "Google User",
            "nonce": challenge.json()["nonce"],
        }

    monkeypatch.setattr(
        "app.services.auth_service._verify_google_credential",
        verified_google_credential,
    )
    payload = {
        "challenge_id": challenge.json()["challenge_id"],
        "credential": "x" * 120,
        "language": "portuguese_br",
    }
    authenticated = await client.post("/auth/google", json=payload)
    assert authenticated.status_code == 200
    assert authenticated.json()["access_token"]

    user = (
        await session.execute(
            select(User).where(User.email == "google-user@example.com")
        )
    ).scalar_one()
    assert user.is_verified is True
    assert user.display_name == "Google User"
    identity = (
        await session.execute(
            select(ExternalIdentity).where(ExternalIdentity.user_id == user.id)
        )
    ).scalar_one()
    assert identity.provider == "google"
    assert identity.subject == "google-subject-123"
    billing_account = (
        await session.execute(
            select(BillingAccount).where(BillingAccount.user_id == user.id)
        )
    ).scalar_one()
    assert billing_account.plan_code == "free"
    assert billing_account.subscription_status == "active"
    assert billing_account.billing_provider == "internal"
    assert billing_account.provider_customer_id is None

    replay = await client.post("/auth/google", json=payload)
    assert replay.status_code == 401
