"""Offline language detection, localization and cost-free routing tests."""

from typing import Any

import pytest

from app.ai.domain.enums import (
    AlfredCapability,
    InternalRoute,
    SelectedSkill,
    capability_for_route,
)
from app.ai.graph import GRAPH_RECURSION_LIMIT, build_graph
from app.ai.graph.state import AgentState
from app.ai.services.language_service import (
    detect_language,
    resolve_response_language,
)
from app.ai.services.routing_service import classify_route


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Como está minha rotina esta semana?", "pt-BR"),
        ("How is my routine going this week?", "en"),
        ("¿Cómo va mi rutina esta semana?", "es"),
        ("Comment évolue ma routine cette semaine ?", "fr"),
    ],
)
def test_offline_detector_handles_the_four_product_languages(
    message: str,
    expected: str,
) -> None:
    result = detect_language(message)

    assert result.language == expected
    assert result.reliable is True
    assert result.source in {"lingua_offline", "product_lexicon_then_lingua"}


@pytest.mark.parametrize("message", ["ok", "kk", "👍"])
def test_language_neutral_short_inputs_do_not_override_preference(message: str) -> None:
    result = detect_language(message)

    assert result.language == "und"
    assert result.reliable is False
    assert resolve_response_language(result.language, "portuguese_br") == "pt-BR"


@pytest.mark.parametrize(
    ("message", "skill", "expected_route"),
    [
        (
            "Quantos hábitos eu concluí hoje?",
            SelectedSkill.AUTO,
            InternalRoute.DETERMINISTIC,
        ),
        (
            "Estou perdendo a motivação.",
            SelectedSkill.AUTO,
            InternalRoute.ALFRED,
        ),
        (
            "Analise meus últimos 30 dias de rotina.",
            SelectedSkill.AUTO,
            InternalRoute.FEEDBACKER,
        ),
        (
            "O que a ciência diz sobre procrastinação?",
            SelectedSkill.AUTO,
            InternalRoute.RAG_THEN_ALFRED,
        ),
        (
            "Analise minha rotina considerando evidências sobre sono.",
            SelectedSkill.AUTO,
            InternalRoute.RAG_THEN_FEEDBACKER,
        ),
    ],
)
def test_canonical_route_examples(
    message: str,
    skill: SelectedSkill,
    expected_route: InternalRoute,
) -> None:
    decision = classify_route(message, skill)

    assert decision.route is expected_route


@pytest.mark.parametrize(
    ("route", "capability"),
    [
        (InternalRoute.DETERMINISTIC, AlfredCapability.DETERMINISTIC),
        (InternalRoute.ALFRED, AlfredCapability.CONVERSATIONAL),
        (InternalRoute.FEEDBACKER, AlfredCapability.ANALYTICAL),
        (
            InternalRoute.RAG_THEN_ALFRED,
            AlfredCapability.KNOWLEDGE_AUGMENTED,
        ),
        (
            InternalRoute.RAG_THEN_FEEDBACKER,
            AlfredCapability.KNOWLEDGE_AUGMENTED,
        ),
        (InternalRoute.SAFE_RESPONSE, None),
    ],
)
def test_every_route_has_an_explicit_product_capability(
    route: InternalRoute,
    capability: AlfredCapability | None,
) -> None:
    assert capability_for_route(route) is capability


def test_message_can_override_a_conflicting_frontend_hint() -> None:
    decision = classify_route(
        "Analise profundamente meus últimos 30 dias de rotina.",
        SelectedSkill.CONVERSAR,
    )

    assert decision.route is InternalRoute.FEEDBACKER
    assert decision.confidence >= 0.9


def test_ambiguous_conversation_is_the_only_case_reserved_for_model_routing() -> None:
    decision = classify_route("Preciso de ajuda.", SelectedSkill.AUTO)

    assert decision.route is InternalRoute.ALFRED
    assert decision.needs_model is True


def _state(message: str) -> AgentState:
    return AgentState(
        request_id="00000000-0000-0000-0000-000000000001",
        user_id="00000000-0000-0000-0000-000000000002",
        conversation_id=None,
        selected_skill=SelectedSkill.AUTO,
        original_input=message,
    )


@pytest.mark.asyncio
async def test_output_localization_does_not_call_a_translation_model() -> None:
    result: dict[str, Any] = dict(
        await build_graph().ainvoke(
            _state("Quantos hábitos eu concluí hoje?"),
            {"recursion_limit": GRAPH_RECURSION_LIMIT},
        )
    )

    assert result["route"] is InternalRoute.DETERMINISTIC
    assert result["response_language"] == "pt-BR"
    assert result["final_response"]["language"] == "pt-BR"
    assert result["final_response"]["translation_applied"] is False
    assert result.get("input_en") is None
    assert result["token_usage"] == {}
