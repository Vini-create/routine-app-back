from collections import defaultdict
from datetime import date, timedelta
from uuid import UUID
from app.core.config import settings

from app.repository import routine_repository as routine_repo
from app.schemas.routine_schemas import (
    GoalCreate,
    GoalUpdate,
    HabitCreate,
    HabitLogCreate,
    HabitUpdate,
    ItemStatus,
    RoutineItemCreate,
    RoutineItemLogCreate,
    RoutineItemsVacationCreate,
    RoutineItemUpdate,
    ScheduleType,
)




def _analysis_end_date(end_date: date) -> date:
    # Avoids lowering consistency because of future days in the selected period.
    return min(end_date, date.today())


def _future_limit_date() -> date:
    # Caps user-created schedules so recurrence expansion stays bounded.
    return date.today() + timedelta(days=365 * settings.future_schedule_limit_years)


def _validate_range(start_date: date, end_date: date, max_days: int, label: str) -> None:
    # Blocks abusive date ranges before recurrence calculations run.
    if end_date < start_date:
        raise ValueError(f"{label} end_date must be greater than or equal to start_date")

    requested_days = (end_date - start_date).days + 1

    if requested_days > max_days:
        raise ValueError(f"{label} range cannot be greater than {max_days} days")


def _validate_not_past(value: date, field_name: str) -> None:
    # Prevents users from creating new schedules that start in the past.
    if value < date.today():
        raise ValueError(f"{field_name} cannot be in the past")


def _validate_not_too_far(value: date, field_name: str) -> None:
    # Prevents schedules from recurring or ending too far in the future.
    if value > _future_limit_date():
        raise ValueError(
            f"{field_name} cannot be more than "
            f"{settings.future_schedule_limit_years} years in the future"
        )


def _schedule_type_value(schedule_type) -> str:
    return schedule_type.value if isinstance(schedule_type, ScheduleType) else schedule_type


def _validate_goal_target_date(target_date: date) -> None:
    # Goals define the natural end date for their habits.
    _validate_not_past(target_date, "target_date")
    _validate_not_too_far(target_date, "target_date")


def _validate_routine_item_create(item_data: RoutineItemCreate) -> None:
    # Routine items cannot start in the past or recur indefinitely.
    _validate_not_past(item_data.start_at.date(), "start_at")
    _validate_not_too_far(item_data.start_at.date(), "start_at")

    if item_data.end_at:
        _validate_not_too_far(item_data.end_at.date(), "end_at")

    if item_data.schedule_type == ScheduleType.RECURRING and item_data.end_at is None:
        raise ValueError("end_at is required for recurring routine items")


def _validate_routine_item_update(routine_item, item_data: RoutineItemUpdate) -> None:
    # Validates only schedule fields affected by the update payload.
    payload = item_data.model_dump(exclude_unset=True)

    if "start_at" in payload:
        _validate_not_past(payload["start_at"].date(), "start_at")
        _validate_not_too_far(payload["start_at"].date(), "start_at")

    if "end_at" in payload and payload["end_at"] is not None:
        _validate_not_too_far(payload["end_at"].date(), "end_at")

    touched_schedule = bool(
        {"schedule_type", "start_at", "end_at", "recurrence_rule"} & payload.keys()
    )

    if not touched_schedule:
        return

    schedule_type = _schedule_type_value(
        payload.get("schedule_type", routine_item.schedule_type)
    )
    end_at = payload.get("end_at", routine_item.end_at)

    if schedule_type == ScheduleType.RECURRING.value and end_at is None:
        raise ValueError("end_at is required for recurring routine items")


def _validate_habit_window(start_date: date, goal) -> None:
    # Habit recurrence is bounded by the selected goal target date.
    if not goal.target_date:
        raise ValueError("Goal target_date is required to create habits")

    _validate_not_too_far(goal.target_date, "goal target_date")

    if goal.target_date < start_date:
        raise ValueError("Habit start_date cannot be after goal target_date")


def _validate_log_date_window(log_date: date) -> None:
    # Keeps daily check-ins honest while still allowing late corrections.
    today = date.today()
    oldest_allowed_date = today - timedelta(days=settings.log_backfill_limit_days)

    if log_date > today:
        raise ValueError("Cannot log future dates")

    if log_date < oldest_allowed_date:
        raise ValueError("Cannot log dates too old")


def _consistency_level(expected_count: int, completed_count: int) -> str:
    # Converts a completion percentage into the visual level used by the frontend.
    if expected_count == 0:
        return "neutral"

    consistency_percent = (completed_count / expected_count) * 100

    if consistency_percent >= 70:
        return "fire"

    if consistency_percent >= 40:
        return "grass"

    return "ice"


def _group_occurrences_by_habit(occurrences: list[dict]) -> dict:
    # Groups expanded habit occurrences so dashboard cards can be built per habit.
    grouped = defaultdict(list)

    for occurrence in occurrences:
        grouped[occurrence["habit"].id].append(occurrence)

    return grouped


def _build_habit_dashboard_item(habit, goal, occurrences: list[dict]) -> dict:
    # Builds one complete habit card with counts, consistency and daily statuses.
    counted_occurrences = [
        occurrence
        for occurrence in occurrences
        if occurrence["status"] != ItemStatus.VACATION.value
    ]
    expected_count = len(counted_occurrences)
    completed_count = sum(
        occurrence["status"] == ItemStatus.COMPLETED.value
        for occurrence in counted_occurrences
    )
    uncompleted_count = sum(
        occurrence["status"] == ItemStatus.UNCOMPLETED.value
        for occurrence in counted_occurrences
    )
    pending_count = sum(
        occurrence["status"] == ItemStatus.PENDING.value
        for occurrence in counted_occurrences
    )
    consistency_percent = (
        round((completed_count / expected_count) * 100, 2)
        if expected_count
        else 0.0
    )

    return {
        "habit": habit,
        "goal": goal,
        "expected_count": expected_count,
        "completed_count": completed_count,
        "uncompleted_count": uncompleted_count,
        "pending_count": pending_count,
        "consistency_percent": consistency_percent,
        "consistency_level": _consistency_level(expected_count, completed_count),
        "occurrences": [
            {
                "date": occurrence["occurrence_date"],
                "status": occurrence["status"],
                "log_id": occurrence["log_id"],
            }
            for occurrence in occurrences
        ],
    }


def _empty_goal_dashboard_item(goal) -> dict:
    # Keeps goals with no habits visible in the goals screen.
    return {
        "goal": goal,
        "expected_count": 0,
        "completed_count": 0,
        "uncompleted_count": 0,
        "pending_count": 0,
        "consistency_percent": 0.0,
        "consistency_level": "neutral",
        "habits": [],
    }


def _build_goal_dashboard_item(goal, habit_items: list[dict]) -> dict:
    # Aggregates habit cards into one goal-level progress card.
    if not habit_items:
        return _empty_goal_dashboard_item(goal)

    expected_count = sum(item["expected_count"] for item in habit_items)
    completed_count = sum(item["completed_count"] for item in habit_items)
    uncompleted_count = sum(item["uncompleted_count"] for item in habit_items)
    pending_count = sum(item["pending_count"] for item in habit_items)
    consistency_percent = (
        round((completed_count / expected_count) * 100, 2)
        if expected_count
        else 0.0
    )

    return {
        "goal": goal,
        "expected_count": expected_count,
        "completed_count": completed_count,
        "uncompleted_count": uncompleted_count,
        "pending_count": pending_count,
        "consistency_percent": consistency_percent,
        "consistency_level": _consistency_level(expected_count, completed_count),
        "habits": habit_items,
    }


async def _routine_item_occurs_on_date(
    session,
    user_id: UUID | str,
    routine_item_id: UUID | str,
    log_date: date,
) -> bool:
    # Confirms the requested log date is a real occurrence of that routine item.
    occurrences = await routine_repo.get_routine_items_by_range(
        session,
        user_id,
        log_date,
        log_date,
    )

    return any(
        occurrence["item"].id == routine_item_id
        for occurrence in occurrences
    )


async def _habit_occurs_on_date(
    session,
    user_id: UUID | str,
    habit_id: UUID | str,
    log_date: date,
) -> bool:
    # Confirms the requested log date is a real occurrence of that habit.
    occurrences = await routine_repo.get_habits_by_range(
        session,
        user_id,
        log_date,
        log_date,
    )

    return any(
        occurrence["habit"].id == habit_id
        for occurrence in occurrences
    )


async def create_goal(session, user_id: UUID | str, goal_data: GoalCreate):
    _validate_goal_target_date(goal_data.target_date)
    return await routine_repo.create_goal(session, user_id, goal_data)


async def list_goals(session, user_id: UUID | str):
    return await routine_repo.list_goals(session, user_id)


async def get_goal(session, user_id: UUID | str, goal_id: UUID | str):
    goal = await routine_repo.get_goal(session, user_id, goal_id)
    if not goal:
        raise ValueError("Goal not found")
    return goal


async def update_goal(
    session,
    user_id: UUID | str,
    goal_id: UUID | str,
    goal_data: GoalUpdate,
):
    if goal_data.target_date is not None:
        _validate_goal_target_date(goal_data.target_date)

    goal = await routine_repo.update_goal(session, user_id, goal_id, goal_data)
    if not goal:
        raise ValueError("Goal not found")
    return goal


async def delete_goal(session, user_id: UUID | str, goal_id: UUID | str) -> None:
    deleted = await routine_repo.delete_goal(session, user_id, goal_id)
    if not deleted:
        raise ValueError("Goal not found")


async def create_routine_item(
    session,
    user_id: UUID | str,
    item_data: RoutineItemCreate,
):
    _validate_routine_item_create(item_data)

    routine_item = await routine_repo.create_routine_item(session, user_id, item_data)
    if not routine_item:
        raise ValueError("Goal not found")
    return routine_item


async def list_routine_items(session, user_id: UUID | str):
    return await routine_repo.list_routine_items(session, user_id)


async def get_routine_item(session, user_id: UUID | str, item_id: UUID | str):
    routine_item = await routine_repo.get_routine_item(session, user_id, item_id)
    if not routine_item:
        raise ValueError("Routine item not found")
    return routine_item


async def update_routine_item(
    session,
    user_id: UUID | str,
    item_id: UUID | str,
    item_data: RoutineItemUpdate,
):
    routine_item = await routine_repo.get_routine_item(session, user_id, item_id)
    if not routine_item:
        raise ValueError("Routine item not found")

    _validate_routine_item_update(routine_item, item_data)

    routine_item = await routine_repo.update_routine_item(
        session,
        user_id,
        item_id,
        item_data,
    )
    if not routine_item:
        raise ValueError("Routine item or goal not found")
    return routine_item


async def delete_routine_item(session, user_id: UUID | str, item_id: UUID | str) -> None:
    deleted = await routine_repo.delete_routine_item(session, user_id, item_id)
    if not deleted:
        raise ValueError("Routine item not found")


async def save_routine_item_log(
    session,
    user_id: UUID | str,
    log_data: RoutineItemLogCreate,
):
    _validate_log_date_window(log_data.log_date)

    if not await _routine_item_occurs_on_date(
        session,
        user_id,
        log_data.routine_item_id,
        log_data.log_date,
    ):
        raise ValueError("Routine item does not occur on this date")

    log = await routine_repo.upsert_routine_item_log(session, user_id, log_data)
    if not log:
        raise ValueError("Routine item not found")
    return log


async def set_routine_items_vacation(
    session,
    user_id: UUID | str,
    payload: RoutineItemsVacationCreate,
):
    _validate_range(
        payload.start_date,
        payload.end_date,
        366 * settings.future_schedule_limit_years,
        "Vacation",
    )
    _validate_not_too_far(payload.end_date, "end_date")

    requested_ids = set(payload.routine_item_ids)
    owned_items = await routine_repo.get_routine_items_by_ids(
        session,
        user_id,
        requested_ids,
    )
    if len(owned_items) != len(requested_ids):
        raise ValueError("One or more routine items were not found")

    occurrences = await routine_repo.get_routine_items_by_range(
        session,
        user_id,
        payload.start_date,
        payload.end_date,
    )
    occurrence_keys = {
        (occurrence["item"].id, occurrence["occurrence_date"])
        for occurrence in occurrences
        if occurrence["item"].id in requested_ids
        and payload.start_date <= occurrence["occurrence_date"] <= payload.end_date
    }
    return await routine_repo.upsert_routine_item_vacation_logs(
        session,
        user_id,
        occurrence_keys,
    )


async def create_habit(session, user_id: UUID | str, habit_data: HabitCreate):
    _validate_not_past(habit_data.start_date, "start_date")
    _validate_not_too_far(habit_data.start_date, "start_date")

    goal = await routine_repo.get_goal(session, user_id, habit_data.goal_id)
    if not goal:
        raise ValueError("Goal not found")

    _validate_habit_window(habit_data.start_date, goal)

    habit = await routine_repo.create_habit(session, user_id, habit_data)
    if not habit:
        raise ValueError("Goal not found")
    return habit


async def list_habits(session, user_id: UUID | str):
    return await routine_repo.list_habits(session, user_id)


async def get_habits_by_goal(session, user_id: UUID | str, goal_id: UUID | str):
    habits = await routine_repo.get_habits_by_goal(session, user_id, goal_id)
    if habits is None:
        raise ValueError("Goal not found")
    return habits


async def get_habit(session, user_id: UUID | str, habit_id: UUID | str):
    habit = await routine_repo.get_habit(session, user_id, habit_id)
    if not habit:
        raise ValueError("Habit not found")
    return habit


async def update_habit(
    session,
    user_id: UUID | str,
    habit_id: UUID | str,
    habit_data: HabitUpdate,
):
    habit = await routine_repo.get_habit(session, user_id, habit_id)
    if not habit:
        raise ValueError("Habit not found")

    payload = habit_data.model_dump(exclude_unset=True)
    goal_id = payload.get("goal_id", habit.goal_id)

    if not goal_id:
        raise ValueError("goal_id is required for habits")

    goal = await routine_repo.get_goal(session, user_id, goal_id)
    if not goal:
        raise ValueError("Goal not found")

    start_date = payload.get("start_date", habit.start_date)

    if "start_date" in payload:
        _validate_not_past(start_date, "start_date")
        _validate_not_too_far(start_date, "start_date")

    _validate_habit_window(start_date, goal)

    habit = await routine_repo.update_habit(session, user_id, habit_id, habit_data)
    if not habit:
        raise ValueError("Habit or goal not found")
    return habit


async def delete_habit(session, user_id: UUID | str, habit_id: UUID | str) -> None:
    deleted = await routine_repo.delete_habit(session, user_id, habit_id)
    if not deleted:
        raise ValueError("Habit not found")


async def save_habit_log(
    session,
    user_id: UUID | str,
    log_data: HabitLogCreate,
):
    _validate_log_date_window(log_data.log_date)

    if not await _habit_occurs_on_date(
        session,
        user_id,
        log_data.habit_id,
        log_data.log_date,
    ):
        raise ValueError("Habit does not occur on this date")

    log = await routine_repo.upsert_habit_log(session, user_id, log_data)
    if not log:
        raise ValueError("Habit not found")
    return log


async def get_routine_agenda(
    session,
    user_id: UUID | str,
    start_date: date,
    end_date: date,
) -> dict:
    _validate_range(
        start_date,
        end_date,
        settings.routine_agenda_max_range_days,
        "Routine agenda",
    )

    routine_occurrences = await routine_repo.get_routine_items_by_range(
        session,
        user_id,
        start_date,
        end_date,
    )
    habit_occurrences = await routine_repo.get_habits_by_range(
        session,
        user_id,
        start_date,
        end_date,
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "routine_items": routine_occurrences,
        "habits": habit_occurrences,
    }


async def get_habits_dashboard(
    session,
    user_id: UUID | str,
    start_date: date,
    end_date: date,
) -> dict:
    # Builds the /habits screen: all user habits with weekly consistency and goal labels.
    _validate_range(
        start_date,
        end_date,
        settings.habits_dashboard_max_range_days,
        "Habits dashboard",
    )

    habits_with_goal = await routine_repo.list_habits_with_goal(session, user_id)
    analysis_end = _analysis_end_date(end_date)

    habit_occurrences = []
    if analysis_end >= start_date:
        habit_occurrences = await routine_repo.get_habits_by_range(
            session,
            user_id,
            start_date,
            analysis_end,
        )

    occurrences_by_habit = _group_occurrences_by_habit(habit_occurrences)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "habits": [
            _build_habit_dashboard_item(
                habit=row["habit"],
                goal=row["goal"],
                occurrences=occurrences_by_habit.get(row["habit"].id, []),
            )
            for row in habits_with_goal
        ],
    }


async def get_goal_habits_dashboard(
    session,
    user_id: UUID | str,
    goal_id: UUID | str,
    start_date: date,
    end_date: date,
) -> list[dict]:
    # Builds the habits section for one goal using the broader goals range limit.
    goal = await get_goal(session, user_id, goal_id)
    analysis_end = _analysis_end_date(end_date)

    _validate_range(
        start_date,
        analysis_end,
        settings.goals_dashboard_max_range_days,
        "Goal habits dashboard",
    )

    habits_with_goal = await routine_repo.list_habits_with_goal(session, user_id)
    habit_occurrences = []

    if analysis_end >= start_date:
        habit_occurrences = await routine_repo.get_habits_by_range(
            session,
            user_id,
            start_date,
            analysis_end,
        )

    occurrences_by_habit = _group_occurrences_by_habit(habit_occurrences)

    return [
        _build_habit_dashboard_item(
            habit=row["habit"],
            goal=goal,
            occurrences=occurrences_by_habit.get(row["habit"].id, []),
        )
        for row in habits_with_goal
        if row["habit"].goal_id == goal.id
    ]


async def get_goals_dashboard(
    session,
    user_id: UUID | str,
    end_date: date,
    start_date: date | None = None,
) -> dict:
    # Builds the /goals screen: goals with their habits and monthly/all-time consistency.
    goals = await routine_repo.list_goals(session, user_id)
    habits_with_goal = await routine_repo.list_habits_with_goal(session, user_id)

    if start_date is None:
        habit_start_dates = [row["habit"].start_date for row in habits_with_goal]
        start_date = min(habit_start_dates) if habit_start_dates else end_date

    analysis_end = _analysis_end_date(end_date)

    _validate_range(
        start_date,
        analysis_end,
        settings.goals_dashboard_max_range_days,
        "Goals dashboard",
    )

    habit_occurrences = []

    if analysis_end >= start_date:
        habit_occurrences = await routine_repo.get_habits_by_range(
            session,
            user_id,
            start_date,
            analysis_end,
        )

    occurrences_by_habit = _group_occurrences_by_habit(habit_occurrences)
    habit_items_by_goal = defaultdict(list)

    for row in habits_with_goal:
        habit = row["habit"]

        if not habit.goal_id:
            continue

        habit_items_by_goal[habit.goal_id].append(
            _build_habit_dashboard_item(
                habit=habit,
                goal=row["goal"],
                occurrences=occurrences_by_habit.get(habit.id, []),
            )
        )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "goals": [
            _build_goal_dashboard_item(
                goal=goal,
                habit_items=habit_items_by_goal.get(goal.id, []),
            )
            for goal in goals
        ],
    }
