from datetime import datetime, timezone

import pytest

from app.ai.domain.enums import SelectedSkill
from app.ai.graph.nodes.deterministic import answer_deterministic_query_node
from app.ai.graph.state import AgentState


@pytest.mark.asyncio
async def test_referential_task_question_lists_names_and_times() -> None:
    today = datetime.now(timezone.utc).date()
    state = AgentState(
        request_id="00000000-0000-0000-0000-000000000001",
        user_id="00000000-0000-0000-0000-000000000002",
        conversation_id=None,
        selected_skill=SelectedSkill.AUTO,
        original_input="Quais são essas 2 tarefas?",
        normalized_input="Quais são essas 2 tarefas?",
        response_language="pt-BR",
        profile={"timezone": "UTC"},
        goals=[],
        habits=[
            {
                "id": "habit-1",
                "name": "Ler documentação",
                "status": "active",
                "start_date": today.isoformat(),
                "recurrence_rule": "FREQ=DAILY",
                "duration_minutes": 25,
                "goal_id": None,
            }
        ],
        routines=[
            {
                "id": "routine-1",
                "title": "Revisar portfólio",
                "status": "active",
                "start_at": datetime.combine(
                    today,
                    datetime.min.time(),
                    tzinfo=timezone.utc,
                )
                .replace(hour=19)
                .isoformat(),
                "end_at": None,
                "schedule_type": "one_time",
                "recurrence_rule": None,
                "duration_minutes": 40,
            }
        ],
        habit_logs=[],
        routine_logs=[],
    )

    result = await answer_deterministic_query_node(state)

    assert "Ler documentação" in result["rendered_response"]
    assert "Revisar portfólio" in result["rendered_response"]
    assert "19:00" in result["rendered_response"]
