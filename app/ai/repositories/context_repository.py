"""Bounded and ownership-scoped reads for the Alfred context pipeline."""

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.models.ai import AIMessage, Feedback
from app.models.auth import User
from app.models.routine import (
    CoachProfile,
    Goal,
    Habit,
    HabitLog,
    RoutineItem,
    RoutineItemLog,
)

MAX_GOALS = 20
MAX_HABITS = 50
MAX_ROUTINE_ITEMS = 75
MAX_LOGS_PER_TYPE = 750
MAX_FEEDBACKS = 10
MAX_MESSAGES = 20
MAX_MESSAGE_CHARS = 2_000


def _iso(value: Any) -> str | None:
    return value.isoformat() if value is not None else None


async def load_user_context(
    session: AsyncSession,
    user_id: UUID,
) -> dict[str, Any]:
    """Load only active data owned by ``user_id`` and cap every collection."""

    user_result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
    )
    user = user_result.scalar_one_or_none()
    if user is None:
        raise AIApplicationError(
            AIErrorCode.USER_CONTEXT_UNAVAILABLE,
            "The authenticated user context is unavailable.",
        )

    coach_result = await session.execute(
        select(CoachProfile)
        .where(CoachProfile.user_id == user_id)
        .order_by(CoachProfile.is_default.desc(), CoachProfile.created_at.desc())
        .limit(1)
    )
    coach = coach_result.scalar_one_or_none()

    goals_result = await session.execute(
        select(Goal)
        .where(
            Goal.user_id == user_id,
            Goal.archived_at.is_(None),
        )
        .order_by(Goal.priority.asc(), Goal.created_at.desc())
        .limit(MAX_GOALS)
    )
    goals = list(goals_result.scalars())

    habits_result = await session.execute(
        select(Habit)
        .where(
            Habit.user_id == user_id,
            Habit.archived_at.is_(None),
        )
        .order_by(Habit.created_at.desc())
        .limit(MAX_HABITS)
    )
    habits = list(habits_result.scalars())

    routines_result = await session.execute(
        select(RoutineItem)
        .where(
            RoutineItem.user_id == user_id,
            RoutineItem.archived_at.is_(None),
        )
        .order_by(RoutineItem.start_at.asc())
        .limit(MAX_ROUTINE_ITEMS)
    )
    routines = list(routines_result.scalars())

    return {
        "profile": {
            "user_id": str(user.id),
            "display_name": user.display_name,
            "timezone": user.timezone,
            "language": user.language,
            "coach": (
                {
                    "id": str(coach.id),
                    "name": coach.name,
                    "style": coach.style,
                    "description": coach.description,
                }
                if coach is not None
                else None
            ),
        },
        "goals": [
            {
                "id": str(goal.id),
                "title": goal.title,
                "description": goal.description,
                "category": goal.category,
                "priority": goal.priority,
                "status": goal.status,
                "target_date": _iso(goal.target_date),
            }
            for goal in goals
        ],
        "habits": [
            {
                "id": str(habit.id),
                "goal_id": str(habit.goal_id) if habit.goal_id else None,
                "name": habit.name,
                "description": habit.description,
                "duration_minutes": habit.duration_minutes,
                "recurrence_rule": habit.recurrence_rule,
                "start_date": _iso(habit.start_date),
                "status": habit.status,
            }
            for habit in habits
        ],
        "routines": [
            {
                "id": str(item.id),
                "goal_id": str(item.goal_id) if item.goal_id else None,
                "title": item.title,
                "description": item.description,
                "item_type": item.item_type,
                "schedule_type": item.schedule_type,
                "start_at": _iso(item.start_at),
                "end_at": _iso(item.end_at),
                "duration_minutes": item.duration_minutes,
                "recurrence_rule": item.recurrence_rule,
                "status": item.status,
            }
            for item in routines
        ],
    }


async def load_history(
    session: AsyncSession,
    user_id: UUID,
    *,
    conversation_id: UUID | None,
    start_date: date,
    end_date: date,
) -> dict[str, Any]:
    """Read bounded execution history; each query repeats the ownership filter."""

    habit_logs_result = await session.execute(
        select(HabitLog)
        .where(
            HabitLog.user_id == user_id,
            HabitLog.log_date.between(start_date, end_date),
        )
        .order_by(HabitLog.log_date.asc(), HabitLog.created_at.asc())
        .limit(MAX_LOGS_PER_TYPE)
    )
    habit_logs = list(habit_logs_result.scalars())

    routine_logs_result = await session.execute(
        select(RoutineItemLog)
        .where(
            RoutineItemLog.user_id == user_id,
            RoutineItemLog.log_date.between(start_date, end_date),
        )
        .order_by(RoutineItemLog.log_date.asc(), RoutineItemLog.created_at.asc())
        .limit(MAX_LOGS_PER_TYPE)
    )
    routine_logs = list(routine_logs_result.scalars())

    feedbacks_result = await session.execute(
        select(Feedback)
        .where(Feedback.user_id == user_id)
        .order_by(Feedback.created_at.desc())
        .limit(MAX_FEEDBACKS)
    )
    feedbacks = list(feedbacks_result.scalars())

    messages: list[AIMessage] = []
    if conversation_id is not None:
        messages_result = await session.execute(
            select(AIMessage)
            .where(
                AIMessage.user_id == user_id,
                AIMessage.conversation_id == conversation_id,
            )
            .order_by(AIMessage.created_at.desc())
            .limit(MAX_MESSAGES)
        )
        messages = list(reversed(list(messages_result.scalars())))

    return {
        "habit_logs": [
            {
                "id": str(log.id),
                "habit_id": str(log.habit_id),
                "log_date": log.log_date.isoformat(),
                "status": log.status,
            }
            for log in habit_logs
        ],
        "routine_logs": [
            {
                "id": str(log.id),
                "routine_item_id": str(log.routine_item_id),
                "log_date": log.log_date.isoformat(),
                "status": log.status,
            }
            for log in routine_logs
        ],
        "previous_feedbacks": [
            {
                "id": str(feedback.id),
                "goal_id": str(feedback.goal_id) if feedback.goal_id else None,
                "content": feedback.content,
                "period_start": feedback.period_start.isoformat(),
                "period_end": feedback.period_end.isoformat(),
                "created_at": feedback.created_at.isoformat(),
            }
            for feedback in feedbacks
        ],
        "recent_messages": [
            {
                "id": str(message.id),
                "role": message.role,
                "content": message.content[:MAX_MESSAGE_CHARS],
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ],
        "history_window": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    }
