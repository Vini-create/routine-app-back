from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

from app.core.security import create_access_token, hash_password, hash_token
from app.models.auth import RefreshToken, User, UserCredential
from app.models.routine import Goal, Habit, HabitLog, RoutineItem, RoutineItemLog
from app.services.auth_service import create_tokens_for_user
from app.services.email_service import EmailDeliveryError


pytestmark = pytest.mark.asyncio


async def create_user(
    session,
    *,
    email: str = "user@example.com",
    display_name: str = "Original name",
    is_verified: bool = True,
) -> User:
    user = User(
        email=email,
        display_name=display_name,
        language="english_us",
        is_active=True,
        is_verified=is_verified,
    )
    session.add(user)
    await session.flush()
    session.add(
        UserCredential(
            user_id=user.id,
            password_hash=hash_password("correct-password"),
        )
    )
    await session.commit()
    await session.refresh(user)
    return user


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(user.id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


async def test_register_reports_email_failure_without_losing_account(client, session, monkeypatch):
    async def fail_delivery(*args, **kwargs):
        raise EmailDeliveryError("provider unavailable")

    monkeypatch.setattr("app.api.auth_routes.send_verification_email", fail_delivery)
    response = await client.post(
        "/auth/register",
        json={
            "email": "pending@example.com",
            "password": "correct-password",
            "display_name": "Pending user",
            "language": "english_us",
        },
    )

    assert response.status_code == 503
    assert "Account created" in response.json()["detail"]
    user = (await session.execute(select(User).where(User.email == "pending@example.com"))).scalar_one()
    assert user.is_verified is False


async def test_resend_verification_is_generic_and_sends_for_pending_user(client, session, monkeypatch):
    pending_user = await create_user(session, email="pending@example.com", is_verified=False)
    delivered_to: list[str] = []

    async def record_delivery(to_email: str, token: str):
        delivered_to.append(to_email)
        assert token

    monkeypatch.setattr("app.services.auth_service.send_verification_email", record_delivery)

    pending = await client.post("/auth/resend-verification", json={"email": pending_user.email})
    missing = await client.post("/auth/resend-verification", json={"email": "missing@example.com"})

    assert pending.status_code == 200
    assert missing.status_code == 200
    assert pending.json() == missing.json()
    assert delivered_to == [pending_user.email]


async def test_patch_me_is_partial_and_validates_fields(client, session):
    user = await create_user(session)

    response = await client.patch(
        "/auth/me",
        headers=auth_headers(user),
        json={"display_name": "Novo nome"},
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Novo nome"
    assert response.json()["language"] == "english_us"

    response = await client.patch(
        "/auth/me",
        headers=auth_headers(user),
        json={"language": "portuguese_br"},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Novo nome"
    assert response.json()["language"] == "portuguese_br"

    invalid_name = await client.patch(
        "/auth/me",
        headers=auth_headers(user),
        json={"display_name": "x"},
    )
    invalid_language = await client.patch(
        "/auth/me",
        headers=auth_headers(user),
        json={"language": "klingon"},
    )
    assert invalid_name.status_code == 422
    assert invalid_language.status_code == 422


async def test_logout_revokes_only_requested_session_and_is_idempotent(client, session):
    user = await create_user(session)
    other_user = await create_user(session, email="other-session@example.com")
    _, first_refresh = await create_tokens_for_user(session, user)
    _, second_refresh = await create_tokens_for_user(session, user)
    _, other_refresh = await create_tokens_for_user(session, other_user)

    first_logout = await client.post(
        "/auth/logout",
        headers=auth_headers(user),
        json={"refresh_token": first_refresh},
    )
    repeated_logout = await client.post(
        "/auth/logout",
        headers=auth_headers(user),
        json={"refresh_token": first_refresh},
    )
    foreign_logout = await client.post(
        "/auth/logout",
        headers=auth_headers(user),
        json={"refresh_token": other_refresh},
    )

    assert first_logout.status_code == 200
    assert repeated_logout.status_code == 200
    assert foreign_logout.status_code == 200

    tokens = {
        token.token_hash: token
        for token in (await session.execute(select(RefreshToken))).scalars().all()
    }
    assert tokens[hash_token(first_refresh)].revoked is True
    assert tokens[hash_token(second_refresh)].revoked is False
    assert tokens[hash_token(other_refresh)].revoked is False

    rejected = await client.post(
        "/auth/refresh",
        json={"refresh_token": first_refresh},
    )
    accepted = await client.post(
        "/auth/refresh",
        json={"refresh_token": second_refresh},
    )
    assert rejected.status_code == 401
    assert accepted.status_code == 200


async def test_vacation_marks_only_real_occurrences_and_is_idempotent(client, session):
    user = await create_user(session)
    start = date.today() + timedelta(days=1)
    start_at = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)
    start_at = start_at.replace(hour=9)
    end = start + timedelta(days=4)
    item = RoutineItem(
        user_id=user.id,
        title="Daily item",
        schedule_type="recurring",
        start_at=start_at,
        end_at=start_at + timedelta(days=4),
        duration_minutes=30,
        recurrence_rule="FREQ=DAILY;INTERVAL=2",
        item_type="task",
        status="active",
    )
    session.add(item)
    await session.flush()
    session.add(
        RoutineItemLog(
            user_id=user.id,
            routine_item_id=item.id,
            log_date=start,
            status="completed",
        )
    )
    await session.commit()

    payload = {
        "routine_item_ids": [str(item.id)],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }
    first = await client.post(
        "/routine/items/vacation",
        headers=auth_headers(user),
        json=payload,
    )
    second = await client.post(
        "/routine/items/vacation",
        headers=auth_headers(user),
        json=payload,
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert len(first.json()) == 3
    assert {row["status"] for row in first.json()} == {"vacation"}
    assert {row["id"] for row in first.json()} == {row["id"] for row in second.json()}

    log_count = await session.scalar(
        select(func.count(RoutineItemLog.id)).where(
            RoutineItemLog.routine_item_id == item.id
        )
    )
    assert log_count == 3

    agenda = await client.get(
        "/routine/agenda",
        headers=auth_headers(user),
        params={"start_date": start.isoformat(), "end_date": end.isoformat()},
    )
    assert agenda.status_code == 200, agenda.text
    assert len(agenda.json()["routine_items"]) == 3
    assert {row["status"] for row in agenda.json()["routine_items"]} == {"vacation"}

    await session.refresh(item)
    assert item.status == "active"
    assert item.archived_at is None


async def test_vacation_is_excluded_from_consistency_counts(client, session):
    user = await create_user(session)
    today = date.today()
    goal = Goal(user_id=user.id, title="Goal", target_date=today + timedelta(days=1))
    session.add(goal)
    await session.flush()
    habit = Habit(
        user_id=user.id,
        goal_id=goal.id,
        name="Habit",
        duration_minutes=10,
        recurrence_rule="FREQ=DAILY",
        start_date=today,
    )
    session.add(habit)
    await session.flush()
    session.add(
        HabitLog(
            user_id=user.id,
            habit_id=habit.id,
            log_date=today,
            status="vacation",
        )
    )
    await session.commit()

    response = await client.get(
        "/routine/habits/dashboard",
        headers=auth_headers(user),
        params={"start_date": today.isoformat(), "end_date": today.isoformat()},
    )

    assert response.status_code == 200, response.text
    metrics = response.json()["habits"][0]
    assert metrics["expected_count"] == 0
    assert metrics["completed_count"] == 0
    assert metrics["uncompleted_count"] == 0
    assert metrics["pending_count"] == 0
    assert metrics["consistency_percent"] == 0.0
    assert metrics["occurrences"][0]["status"] == "vacation"


async def test_vacation_rejects_items_from_another_user_without_writes(client, session):
    user = await create_user(session)
    other_user = await create_user(session, email="other@example.com")
    tomorrow = date.today() + timedelta(days=1)
    other_item = RoutineItem(
        user_id=other_user.id,
        title="Not mine",
        schedule_type="single",
        start_at=datetime.combine(tomorrow, datetime.min.time(), tzinfo=timezone.utc),
        duration_minutes=10,
        item_type="task",
        status="active",
    )
    session.add(other_item)
    await session.commit()

    response = await client.post(
        "/routine/items/vacation",
        headers=auth_headers(user),
        json={
            "routine_item_ids": [str(other_item.id)],
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == 400
    assert await session.scalar(select(func.count(RoutineItemLog.id))) == 0


async def test_account_deletion_revokes_tokens_and_blocks_old_access(client, session):
    user = await create_user(session)
    access_headers = auth_headers(user)
    _, first_refresh = await create_tokens_for_user(session, user)
    _, second_refresh = await create_tokens_for_user(session, user)
    today = date.today()

    goal = Goal(user_id=user.id, title="Goal", target_date=today + timedelta(days=30))
    session.add(goal)
    await session.flush()
    habit = Habit(
        user_id=user.id,
        goal_id=goal.id,
        name="Habit",
        duration_minutes=10,
        recurrence_rule="FREQ=DAILY",
        start_date=today,
    )
    item = RoutineItem(
        user_id=user.id,
        goal_id=goal.id,
        title="Item",
        schedule_type="single",
        start_at=datetime.now(timezone.utc),
        duration_minutes=10,
    )
    session.add_all([habit, item])
    await session.flush()
    session.add_all(
        [
            HabitLog(user_id=user.id, habit_id=habit.id, log_date=today, status="completed"),
            RoutineItemLog(
                user_id=user.id,
                routine_item_id=item.id,
                log_date=today,
                status="completed",
            ),
        ]
    )
    await session.commit()

    deleted = await client.delete("/users/me", headers=access_headers)
    assert deleted.status_code == 200

    await session.refresh(user)
    assert user.is_active is False
    assert user.pending_deletion is True
    assert user.deleted_at is not None
    assert all(
        token.revoked
        for token in (await session.execute(select(RefreshToken))).scalars().all()
    )

    assert await session.scalar(select(func.count(Goal.id))) == 1
    assert await session.scalar(select(func.count(Habit.id))) == 1
    assert await session.scalar(select(func.count(RoutineItem.id))) == 1
    assert await session.scalar(select(func.count(HabitLog.id))) == 1
    assert await session.scalar(select(func.count(RoutineItemLog.id))) == 1

    old_access = await client.get("/auth/me", headers=access_headers)
    first_refresh_response = await client.post(
        "/auth/refresh", json={"refresh_token": first_refresh}
    )
    second_refresh_response = await client.post(
        "/auth/refresh", json={"refresh_token": second_refresh}
    )
    login = await client.post(
        "/auth/login",
        json={"email": user.email, "password": "correct-password"},
    )
    assert old_access.status_code == 401
    assert first_refresh_response.status_code == 401
    assert second_refresh_response.status_code == 401
    assert login.status_code == 401
