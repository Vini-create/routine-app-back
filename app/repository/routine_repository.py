from datetime import date, datetime, time, timedelta, timezone
from enum import Enum
from uuid import UUID

from sqlalchemy import and_, or_, select

from app.models.routine import Goal, Habit, HabitLog, RoutineItem, RoutineItemLog
from app.schemas.routine_schemas import (
    GoalCreate,
    GoalUpdate,
    HabitCreate,
    HabitLogCreate,
    HabitUpdate,
    RoutineItemCreate,
    RoutineItemLogCreate,
    RoutineItemUpdate,
)
from app.services.recurrence import get_occurrences


def _range_bounds(start_date: date, end_date: date) -> tuple[datetime, datetime]:
    if end_date < start_date:
        raise ValueError("end_date must be greater than or equal to start_date")

    range_start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    range_end = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return range_start, range_end


def _plain_value(value):
    return value.value if isinstance(value, Enum) else value


def _plain_payload(payload: dict) -> dict:
    return {key: _plain_value(value) for key, value in payload.items()}


def _routine_item_payload(data: RoutineItemCreate | RoutineItemUpdate) -> dict:
    return _plain_payload(data.model_dump(exclude_unset=True))


async def _goal_belongs_to_user(session, user_id: UUID | str, goal_id: UUID | str) -> bool:
    result = await session.execute(
        select(Goal.id).where(
            Goal.id == goal_id,
            Goal.user_id == user_id,
            Goal.archived_at.is_(None),
        )
    )
    return result.scalar_one_or_none() is not None


async def create_goal(session, user_id: UUID | str, goal_data: GoalCreate) -> Goal:
    goal = Goal(user_id=user_id, **_plain_payload(goal_data.model_dump()))
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal


async def list_goals(session, user_id: UUID | str) -> list[Goal]:
    result = await session.execute(
        select(Goal)
        .where(Goal.user_id == user_id, Goal.archived_at.is_(None))
        .order_by(Goal.created_at.desc())
    )
    return list(result.scalars().all())


async def get_goal(session, user_id: UUID | str, goal_id: UUID | str) -> Goal | None:
    result = await session.execute(
        select(Goal).where(
            Goal.id == goal_id,
            Goal.user_id == user_id,
            Goal.archived_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_goal(
    session,
    user_id: UUID | str,
    goal_id: UUID | str,
    goal_data: GoalUpdate,
) -> Goal | None:
    goal = await get_goal(session, user_id, goal_id)
    if not goal:
        return None

    for field, value in _plain_payload(goal_data.model_dump(exclude_unset=True)).items():
        setattr(goal, field, value)

    await session.commit()
    await session.refresh(goal)
    return goal


async def delete_goal(session, user_id: UUID | str, goal_id: UUID | str) -> bool:
    goal = await get_goal(session, user_id, goal_id)
    if not goal:
        return False

    await session.delete(goal)
    await session.commit()
    return True


async def create_routine_item(
    session,
    user_id: UUID | str,
    item_data: RoutineItemCreate,
) -> RoutineItem | None:
    payload = _routine_item_payload(item_data)
    goal_id = payload.get("goal_id")

    if goal_id and not await _goal_belongs_to_user(session, user_id, goal_id):
        return None

    routine_item = RoutineItem(user_id=user_id, **payload)
    session.add(routine_item)
    await session.commit()
    await session.refresh(routine_item)
    return routine_item


async def list_routine_items(session, user_id: UUID | str) -> list[RoutineItem]:
    result = await session.execute(
        select(RoutineItem)
        .where(RoutineItem.user_id == user_id, RoutineItem.archived_at.is_(None))
        .order_by(RoutineItem.start_at.asc())
    )
    return list(result.scalars().all())


async def get_routine_item(
    session,
    user_id: UUID | str,
    item_id: UUID | str,
) -> RoutineItem | None:
    result = await session.execute(
        select(RoutineItem).where(
            RoutineItem.id == item_id,
            RoutineItem.user_id == user_id,
            RoutineItem.archived_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_routine_items_by_ids(
    session,
    user_id: UUID | str,
    item_ids: set[UUID],
) -> list[RoutineItem]:
    result = await session.execute(
        select(RoutineItem).where(
            RoutineItem.id.in_(item_ids),
            RoutineItem.user_id == user_id,
            RoutineItem.archived_at.is_(None),
        )
    )
    return list(result.scalars().all())


async def update_routine_item(
    session,
    user_id: UUID | str,
    item_id: UUID | str,
    item_data: RoutineItemUpdate,
) -> RoutineItem | None:
    routine_item = await get_routine_item(session, user_id, item_id)
    if not routine_item:
        return None

    payload = _routine_item_payload(item_data)
    goal_id = payload.get("goal_id")

    if goal_id and not await _goal_belongs_to_user(session, user_id, goal_id):
        return None

    for field, value in payload.items():
        setattr(routine_item, field, value)

    await session.commit()
    await session.refresh(routine_item)
    return routine_item


async def delete_routine_item(session, user_id: UUID | str, item_id: UUID | str) -> bool:
    routine_item = await get_routine_item(session, user_id, item_id)
    if not routine_item:
        return False

    await session.delete(routine_item)
    await session.commit()
    return True


async def get_routine_items_by_range(
    session,
    user_id: UUID | str,
    start_date: date,
    end_date: date,
) -> list[dict]:
    range_start, range_end = _range_bounds(start_date, end_date)

    result = await session.execute(
        select(RoutineItem).where(
            RoutineItem.user_id == user_id,
            RoutineItem.archived_at.is_(None),
            RoutineItem.status == "active",
            or_(
                (
                    (RoutineItem.schedule_type == "single")
                    & (RoutineItem.start_at >= range_start)
                    & (RoutineItem.start_at < range_end)
                ),
                (
                    (RoutineItem.schedule_type == "recurring")
                    & (RoutineItem.start_at < range_end)
                    & (
                        RoutineItem.end_at.is_(None)
                        | (RoutineItem.end_at >= range_start)
                    )
                ),
            ),
        )
    )

    occurrences = []

    logs_result = await session.execute(
        select(RoutineItemLog).where(
            RoutineItemLog.user_id == user_id,
            RoutineItemLog.log_date >= start_date,
            RoutineItemLog.log_date <= end_date,
        )
    )
    logs_index = {
        (log.routine_item_id, log.log_date): log
        for log in logs_result.scalars().all()
    }

    for item in result.scalars().all():
        if item.schedule_type == "single":
            log = logs_index.get((item.id, item.start_at.date()))

            occurrences.append(
                {
                    "item": item,
                    "occurrence_at": item.start_at,
                    "occurrence_date": item.start_at.date(),
                    "status": log.status if log else "pending",
                    "log_id": log.id if log else None,
                }
            )
            continue

        if item.recurrence_rule:
            item_range_end = range_end
            if item.end_at is not None:
                item_range_end = min(item_range_end, item.end_at)

            for occurrence in get_occurrences(
                item.recurrence_rule,
                item.start_at,
                range_start,
                item_range_end,
            ):
                # rrule.between is inclusive; the API's upper bound is not.
                if occurrence >= range_end:
                    continue
                log = logs_index.get((item.id, occurrence.date()))

                occurrences.append(
                    {
                        "item": item,
                        "occurrence_at": occurrence,
                        "occurrence_date": occurrence.date(),
                        "status": log.status if log else "pending",
                        "log_id": log.id if log else None,
                    }
                )

    return sorted(occurrences, key=lambda row: row["occurrence_at"])


async def upsert_routine_item_log(
    session,
    user_id: UUID | str,
    log_data: RoutineItemLogCreate,
) -> RoutineItemLog | None:
    routine_item = await get_routine_item(session, user_id, log_data.routine_item_id)
    if not routine_item:
        return None

    result = await session.execute(
        select(RoutineItemLog).where(
            RoutineItemLog.user_id == user_id,
            RoutineItemLog.routine_item_id == log_data.routine_item_id,
            RoutineItemLog.log_date == log_data.log_date,
        )
    )
    log = result.scalar_one_or_none()

    if log:
        log.status = _plain_value(log_data.status)
    else:
        log = RoutineItemLog(
            user_id=user_id,
            routine_item_id=log_data.routine_item_id,
            log_date=log_data.log_date,
            status=_plain_value(log_data.status),
        )
        session.add(log)

    await session.commit()
    await session.refresh(log)
    return log


async def upsert_routine_item_vacation_logs(
    session,
    user_id: UUID | str,
    occurrence_keys: set[tuple[UUID, date]],
) -> list[RoutineItemLog]:
    if not occurrence_keys:
        return []

    item_ids = {item_id for item_id, _ in occurrence_keys}
    dates = {log_date for _, log_date in occurrence_keys}
    result = await session.execute(
        select(RoutineItemLog).where(
            RoutineItemLog.user_id == user_id,
            RoutineItemLog.routine_item_id.in_(item_ids),
            RoutineItemLog.log_date.in_(dates),
        )
    )
    existing = {
        (log.routine_item_id, log.log_date): log
        for log in result.scalars().all()
    }

    logs = []
    for item_id, log_date in sorted(occurrence_keys, key=lambda key: (key[1], str(key[0]))):
        log = existing.get((item_id, log_date))
        if log is None:
            log = RoutineItemLog(
                user_id=user_id,
                routine_item_id=item_id,
                log_date=log_date,
                status="vacation",
            )
            session.add(log)
        else:
            log.status = "vacation"
        logs.append(log)

    await session.commit()
    for log in logs:
        await session.refresh(log)
    return logs

async def create_habit(
    session,
    user_id: UUID | str,
    habit_data: HabitCreate,
) -> Habit | None:
    payload = _plain_payload(habit_data.model_dump())
    goal_id = payload.get("goal_id")

    if goal_id and not await _goal_belongs_to_user(session, user_id, goal_id):
        return None

    habit = Habit(user_id=user_id, **payload)
    session.add(habit)
    await session.commit()
    await session.refresh(habit)
    return habit


async def list_habits(session, user_id: UUID | str) -> list[Habit]:
    result = await session.execute(
        select(Habit)
        .where(Habit.user_id == user_id, Habit.archived_at.is_(None))
        .order_by(Habit.created_at.desc())
    )
    return list(result.scalars().all())


async def list_habits_with_goal(session, user_id: UUID | str) -> list[dict]:
    # Returns every active habit with its optional goal label for the habits screen.
    result = await session.execute(
        select(Habit, Goal)
        .outerjoin(
            Goal,
            and_(
                Habit.goal_id == Goal.id,
                Goal.archived_at.is_(None),
            ),
        )
        .where(Habit.user_id == user_id, Habit.archived_at.is_(None))
        .order_by(Habit.created_at.desc())
    )

    return [
        {
            "habit": habit,
            "goal": goal,
        }
        for habit, goal in result.all()
    ]


async def get_habits_by_goal(
    session,
    user_id: UUID | str,
    goal_id: UUID | str,
) -> list[Habit] | None:
    if not await _goal_belongs_to_user(session, user_id, goal_id):
        return None

    result = await session.execute(
        select(Habit)
        .where(
            Habit.user_id == user_id,
            Habit.goal_id == goal_id,
            Habit.archived_at.is_(None),
        )
        .order_by(Habit.created_at.desc())
    )
    return list(result.scalars().all())


async def get_habit(session, user_id: UUID | str, habit_id: UUID | str) -> Habit | None:
    result = await session.execute(
        select(Habit).where(
            Habit.id == habit_id,
            Habit.user_id == user_id,
            Habit.archived_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_habit(
    session,
    user_id: UUID | str,
    habit_id: UUID | str,
    habit_data: HabitUpdate,
) -> Habit | None:
    habit = await get_habit(session, user_id, habit_id)
    if not habit:
        return None

    payload = _plain_payload(habit_data.model_dump(exclude_unset=True))
    goal_id = payload.get("goal_id")

    if goal_id and not await _goal_belongs_to_user(session, user_id, goal_id):
        return None

    for field, value in payload.items():
        setattr(habit, field, value)

    await session.commit()
    await session.refresh(habit)
    return habit


async def delete_habit(session, user_id: UUID | str, habit_id: UUID | str) -> bool:
    habit = await get_habit(session, user_id, habit_id)
    if not habit:
        return False

    await session.delete(habit)
    await session.commit()
    return True


async def get_habits_by_range(
    session,
    user_id: UUID | str,
    start_date: date,
    end_date: date,
) -> list[dict]:
    range_start, range_end = _range_bounds(start_date, end_date)

    result = await session.execute(
        select(Habit, Goal)
        .outerjoin(
            Goal,
            and_(
                Habit.goal_id == Goal.id,
                Goal.archived_at.is_(None),
            ),
        )
        .where(
            Habit.user_id == user_id,
            Habit.archived_at.is_(None),
            Habit.status == "active",
            Habit.start_date <= end_date,
            Goal.target_date.is_not(None),
            Goal.target_date >= start_date,
        )
    )

    occurrences = []

    logs_result = await session.execute(
        select(HabitLog).where(
            HabitLog.user_id == user_id,
            HabitLog.log_date >= start_date,
            HabitLog.log_date <= end_date,
        )
    )
    logs_index = {
        (log.habit_id, log.log_date): log
        for log in logs_result.scalars().all()
    }

    for habit, goal in result.all():
        habit_start_at = datetime.combine(habit.start_date, time.min, tzinfo=timezone.utc)
        habit_range_end = min(
            range_end,
            datetime.combine(goal.target_date + timedelta(days=1), time.min, tzinfo=timezone.utc),
        )

        if habit_range_end <= range_start:
            continue

        for occurrence in get_occurrences(
            habit.recurrence_rule,
            habit_start_at,
            range_start,
            habit_range_end,
        ):
            # habit_range_end is an exclusive API/goal boundary, while
            # rrule.between(..., inc=True) includes it.
            if occurrence >= habit_range_end:
                continue
            log = logs_index.get((habit.id, occurrence.date()))

            occurrences.append(
                {
                    "habit": habit,
                    "goal": goal,
                    "occurrence_date": occurrence.date(),
                    "status": log.status if log else "pending",
                    "log_id": log.id if log else None,
                }
            )

    return sorted(occurrences, key=lambda row: row["occurrence_date"])


async def get_habits_by_day(
    session,
    user_id: UUID | str,
    day: date,
) -> list[dict]:
    return await get_habits_by_range(session, user_id, day, day)


async def upsert_habit_log(
    session,
    user_id: UUID | str,
    log_data: HabitLogCreate,
) -> HabitLog | None:
    habit = await get_habit(session, user_id, log_data.habit_id)
    if not habit:
        return None

    result = await session.execute(
        select(HabitLog).where(
            HabitLog.user_id == user_id,
            HabitLog.habit_id == log_data.habit_id,
            HabitLog.log_date == log_data.log_date,
        )
    )
    log = result.scalar_one_or_none()

    if log:
        log.status = _plain_value(log_data.status)
    else:
        log = HabitLog(
            user_id=user_id,
            habit_id=log_data.habit_id,
            log_date=log_data.log_date,
            status=_plain_value(log_data.status),
        )
        session.add(log)

    await session.commit()
    await session.refresh(log)
    return log
