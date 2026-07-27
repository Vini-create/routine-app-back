"""Integration and unit tests for Stage 4 context and behavioral intelligence."""

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import pytest
from langgraph.runtime import Runtime

from app.ai.domain.enums import InternalRoute, SelectedSkill
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.graph import (
    GRAPH_RECURSION_LIMIT,
    GraphRuntimeContext,
    build_graph,
)
from app.ai.graph.nodes.context import load_user_context_node
from app.ai.graph.state import AgentState
from app.ai.services.behavior_service import (
    calculate_behavior_metrics,
    detect_behavior_anomalies,
    detect_behavior_trends,
    predict_dropout_risk,
)
from app.models.ai import AIConversation, AIMessage, Feedback
from app.models.auth import User
from app.models.routine import Goal, Habit, HabitLog, RoutineItem, RoutineItemLog

NOW = datetime(2026, 7, 29, 12, tzinfo=timezone.utc)


def graph_state(
    user_id: UUID,
    conversation_id: UUID | None = None,
) -> AgentState:
    return AgentState(
        request_id=str(uuid4()),
        user_id=str(user_id),
        conversation_id=str(conversation_id) if conversation_id else None,
        selected_skill=SelectedSkill.AUTO,
        original_input="Quantos hábitos eu concluí?",
        route=InternalRoute.DETERMINISTIC,
    )


def declining_context() -> dict:
    completed_dates = {
        date(2026, 7, day).isoformat() for day in (*range(1, 8), *range(9, 22))
    }
    return {
        "profile": {"timezone": "UTC"},
        "goals": [
            {
                "id": "goal-1",
                "target_date": "2026-08-31",
            }
        ],
        "habits": [
            {
                "id": "habit-1",
                "goal_id": "goal-1",
                "name": "Estudar",
                "duration_minutes": 30,
                "recurrence_rule": "FREQ=DAILY",
                "start_date": "2026-07-01",
                "status": "active",
            }
        ],
        "routines": [],
        "habit_logs": [
            {
                "habit_id": "habit-1",
                "log_date": item,
                "status": "completed",
            }
            for item in sorted(completed_dates)
        ]
        + [
            {
                "habit_id": "habit-1",
                "log_date": "2026-07-08",
                "status": "vacation",
            }
        ],
        "routine_logs": [],
    }


def test_metrics_exclude_today_and_vacation_from_denominator() -> None:
    metrics = calculate_behavior_metrics(declining_context(), now=NOW)

    assert metrics["window"] == {
        "start_date": "2026-07-01",
        "end_date": "2026-07-28",
        "days": 28,
        "excludes_current_day": True,
    }
    assert metrics["summary"]["expected_count"] == 27
    assert metrics["summary"]["completed_count"] == 20
    assert metrics["summary"]["vacation_count"] == 1
    assert metrics["summary"]["completion_rate"] == pytest.approx(20 / 27, abs=1e-4)
    assert metrics["entities"][0]["longest_streak"] == 20


def test_trends_anomalies_and_dropout_risk_are_explainable() -> None:
    metrics = calculate_behavior_metrics(declining_context(), now=NOW)
    trends = detect_behavior_trends(metrics)
    anomalies = detect_behavior_anomalies(metrics, trends)
    risk = predict_dropout_risk(metrics, trends, anomalies)

    assert trends[0]["direction"] == "declining"
    assert {item["type"] for item in anomalies} >= {
        "completion_drop",
        "recent_inactivity",
    }
    assert risk["level"] == "moderate"
    assert risk["score"] == pytest.approx(0.5)
    assert risk["method"] == "transparent_rules_v1"
    assert risk["is_clinical_prediction"] is False


@pytest.mark.asyncio
async def test_runtime_identity_mismatch_fails_before_database_read(session) -> None:
    authenticated_id = uuid4()
    different_state_id = uuid4()
    runtime = Runtime(
        context=GraphRuntimeContext(
            session=session,
            authenticated_user_id=authenticated_id,
            now=NOW,
        )
    )

    with pytest.raises(AIApplicationError) as error:
        await load_user_context_node(graph_state(different_state_id), runtime)

    assert error.value.code is AIErrorCode.USER_CONTEXT_FORBIDDEN


@pytest.mark.asyncio
async def test_graph_loads_only_authenticated_user_and_builds_behavior(session) -> None:
    user_id = uuid4()
    other_user_id = uuid4()
    user = User(
        id=user_id,
        email="context-owner@example.com",
        display_name="Context Owner",
        timezone="UTC",
        language="pt-BR",
    )
    other = User(
        id=other_user_id,
        email="other-context@example.com",
        display_name="Other",
        timezone="UTC",
        language="en",
    )
    session.add_all([user, other])
    await session.flush()

    goal = Goal(
        id=uuid4(),
        user_id=user_id,
        title="Portfólio",
        category="career",
        priority=1,
        status="in_progress",
        target_date=date(2026, 8, 31),
    )
    other_goal = Goal(
        id=uuid4(),
        user_id=other_user_id,
        title="Should never leak",
        priority=1,
        status="in_progress",
        target_date=date(2026, 8, 31),
    )
    habit = Habit(
        id=uuid4(),
        user_id=user_id,
        goal_id=goal.id,
        name="Implementar",
        duration_minutes=45,
        recurrence_rule="FREQ=DAILY",
        start_date=date(2026, 7, 1),
        status="active",
    )
    routine = RoutineItem(
        id=uuid4(),
        user_id=user_id,
        goal_id=goal.id,
        title="Revisão semanal",
        item_type="task",
        schedule_type="recurring",
        start_at=datetime(2026, 7, 1, 9, tzinfo=timezone.utc),
        duration_minutes=60,
        recurrence_rule="FREQ=WEEKLY",
        status="active",
    )
    session.add_all([goal, other_goal, habit, routine])
    await session.flush()
    conversation = AIConversation(
        user_id=user_id,
        title="Revisão de progresso",
    )
    session.add(conversation)
    await session.flush()
    session.add_all(
        [
            HabitLog(
                habit_id=habit.id,
                user_id=user_id,
                log_date=date(2026, 7, 1),
                status="completed",
            ),
            RoutineItemLog(
                routine_item_id=routine.id,
                user_id=user_id,
                log_date=date(2026, 7, 1),
                status="completed",
            ),
            AIMessage(
                conversation_id=conversation.id,
                user_id=user_id,
                role="user",
                content="Quero revisar meu progresso.",
                request_id=uuid4(),
                route=InternalRoute.ALFRED.value,
                created_at=datetime(2026, 7, 20, tzinfo=timezone.utc),
            ),
            Feedback(
                user_id=user_id,
                goal_id=goal.id,
                content={"summary": "Primeira análise"},
                period_start=date(2026, 7, 1),
                period_end=date(2026, 7, 14),
                created_at=datetime(2026, 7, 15, tzinfo=timezone.utc),
            ),
        ]
    )
    await session.commit()

    result = await build_graph().ainvoke(
        graph_state(user_id, conversation.id),
        {"recursion_limit": GRAPH_RECURSION_LIMIT},
        context=GraphRuntimeContext(
            session=session,
            authenticated_user_id=user_id,
            now=NOW,
        ),
    )

    assert result["profile"]["display_name"] == "Context Owner"
    assert [item["title"] for item in result["goals"]] == ["Portfólio"]
    assert "Should never leak" not in str(result["user_context"])
    assert result["habit_logs"][0]["habit_id"] == str(habit.id)
    assert result["routine_logs"][0]["routine_item_id"] == str(routine.id)
    assert result["recent_messages"][0]["content"] == ("Quero revisar meu progresso.")
    assert result["habit_metrics"]["summary"]["expected_count"] == 32
    assert result["behavioral_state"]["methodology"]["uses_llm"] is False
    assert result["dropout_risk"]["method"] == "transparent_rules_v1"
    assert "memory_store" not in result["unavailable_components"]
    assert result["relevant_memories"] == []
    assert (
        result["user_context"]["trust_boundaries"]["messages_feedbacks_and_memories"]
        == "untrusted_user_content"
    )
