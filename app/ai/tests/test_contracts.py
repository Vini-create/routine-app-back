"""Contract tests for stage 1 of the unified Alfred graph."""

from uuid import uuid4

import pytest
from langgraph.graph import StateGraph
from pydantic import ValidationError

from app.ai.domain.enums import (
    AlfredCapability,
    InternalRoute,
    SafetyLevel,
    SelectedSkill,
)
from app.ai.graph.state import AgentState
from app.ai.schemas.analysis import (
    AnalysisReport,
    ExecutionDiagnosis,
    IdentifiedPattern,
    RootCauseHypothesis,
)
from app.ai.schemas.patches import PatchOperation, ProposedPatch
from app.ai.schemas.requests import (
    MAX_INPUT_CHARS,
    MAX_SCREEN_CONTEXT_BYTES,
    AIInvokeRequest,
)
from app.ai.schemas.responses import AIInvokeResponse, AIUsage
from app.ai.schemas.retrieval import EvidenceReference
from app.ai.schemas.routing import RoutingDecision
from app.ai.schemas.safety import SafetyAssessment


def build_usage() -> AIUsage:
    return AIUsage(
        plan="free",
        units_reserved=1,
        units_consumed=1,
        units_remaining=29,
    )


def build_patch() -> ProposedPatch:
    return ProposedPatch(
        patch_id=uuid4(),
        entity_type="habit",
        entity_id=uuid4(),
        operations=[
            PatchOperation(op="replace", path="/frequency", value=3),
        ],
        reason="A frequência atual está acima da capacidade observada.",
    )


def test_selected_skill_is_only_a_public_hint() -> None:
    assert [skill.value for skill in SelectedSkill] == [
        "auto",
        "conversar",
        "analisar_progresso",
        "reorganizar_rotina",
        "criar_plano",
        "consultar_conhecimento",
    ]
    assert "feedbacker" not in {skill.value for skill in SelectedSkill}
    assert "alfred" not in {skill.value for skill in SelectedSkill}


def test_alfred_has_four_architectural_capabilities() -> None:
    assert {capability.value for capability in AlfredCapability} == {
        "deterministic",
        "conversational",
        "analytical",
        "knowledge_augmented",
    }


def test_internal_routes_match_the_graph_contract() -> None:
    assert {route.value for route in InternalRoute} == {
        "safe_response",
        "deterministic",
        "alfred",
        "feedbacker",
        "rag_then_alfred",
        "rag_then_feedbacker",
    }
    assert "blocked" not in {route.value for route in InternalRoute}


def test_invoke_request_uses_safe_defaults_and_normalizes_strings() -> None:
    request = AIInvokeRequest(message="  Quero revisar minha rotina.  ")

    assert request.message == "Quero revisar minha rotina."
    assert request.selected_skill is SelectedSkill.AUTO
    assert request.conversation_id is None
    assert request.screen_context is None


@pytest.mark.parametrize("message", ["", " ", "\n\t"])
def test_invoke_request_rejects_blank_messages(message: str) -> None:
    with pytest.raises(ValidationError):
        AIInvokeRequest(message=message)


def test_invoke_request_enforces_free_plan_input_limit() -> None:
    AIInvokeRequest(message="a" * MAX_INPUT_CHARS)

    with pytest.raises(ValidationError):
        AIInvokeRequest(message="a" * (MAX_INPUT_CHARS + 1))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("request_type", "feedbacker"),
        ("selected_mode", "feedbacker"),
        ("selected_skill", "feedbacker"),
        ("selected_skill", "alfred"),
    ],
)
def test_invoke_request_rejects_legacy_public_routing(
    field: str,
    value: str,
) -> None:
    payload = {"message": "Analise meu progresso.", field: value}

    with pytest.raises(ValidationError):
        AIInvokeRequest.model_validate(payload)


def test_invoke_request_limits_screen_context_size() -> None:
    small_context = {"page": "habits", "selected_ids": ["habit-1"]}
    request = AIInvokeRequest(message="Ajude-me.", screen_context=small_context)
    assert request.screen_context == small_context

    oversized = {"content": "ç" * MAX_SCREEN_CONTEXT_BYTES}
    with pytest.raises(ValidationError, match="screen_context cannot exceed"):
        AIInvokeRequest(message="Ajude-me.", screen_context=oversized)


def test_invoke_request_rejects_non_json_screen_context() -> None:
    with pytest.raises(ValidationError, match="JSON serializable"):
        AIInvokeRequest(
            message="Ajude-me.",
            screen_context={"invalid": object()},
        )


def test_routing_decision_validates_confidence_range() -> None:
    decision = RoutingDecision(
        detected_intent="analisar_rotina",
        intent_confidence=0.91,
        route=InternalRoute.FEEDBACKER,
        route_confidence=0.88,
        route_reason="A mensagem pede uma análise longitudinal.",
    )
    assert decision.route is InternalRoute.FEEDBACKER

    with pytest.raises(ValidationError):
        RoutingDecision(
            detected_intent="analisar_rotina",
            intent_confidence=1.01,
            route=InternalRoute.FEEDBACKER,
            route_confidence=0.88,
            route_reason="Confiança inválida.",
        )


def test_safety_contract_keeps_personal_risk_and_injection_separate() -> None:
    assessment = SafetyAssessment(
        level=SafetyLevel.HIGH,
        categories=["self_harm"],
        risk_score=0.9,
        blocked=True,
        prompt_injection_suspected=False,
        prompt_injection_score=0,
    )

    assert assessment.blocked is True
    assert assessment.prompt_injection_suspected is False


def test_hypothesis_requires_explicit_bounded_confidence() -> None:
    hypothesis = RootCauseHypothesis(
        hypothesis="A carga planejada pode estar acima da capacidade recente.",
        supporting_evidence=["Queda de conclusão nas últimas duas semanas."],
        confidence=0.65,
    )
    assert hypothesis.confidence == 0.65

    with pytest.raises(ValidationError):
        RootCauseHypothesis(
            hypothesis="Causa absoluta.",
            confidence=2,
        )


def test_analysis_report_uses_independent_collection_defaults() -> None:
    diagnosis = ExecutionDiagnosis(
        summary="Execução estável.",
        data_window="last_30_days",
        data_quality=0.8,
    )
    first = AnalysisReport(diagnosis=diagnosis)
    second = AnalysisReport(diagnosis=diagnosis)

    first.patterns.append(
        IdentifiedPattern(
            name="Consistência",
            description="Padrão estável.",
            confidence=0.8,
        )
    )
    assert second.patterns == []


@pytest.mark.parametrize("path", ["frequency", "//frequency", "/"])
def test_patch_operation_rejects_invalid_json_pointer(path: str) -> None:
    with pytest.raises(ValidationError):
        PatchOperation(op="replace", path=path, value=3)


def test_public_response_requires_persisted_patch_and_confirmation_together() -> None:
    base = {
        "request_id": uuid4(),
        "conversation_id": uuid4(),
        "route": InternalRoute.FEEDBACKER,
        "message": "Encontrei uma oportunidade de ajuste.",
        "usage": build_usage(),
    }

    patch = build_patch()
    response = AIInvokeResponse.model_validate(
        {
            **base,
            "proposed_patch": patch,
            "requires_confirmation": True,
        }
    )
    assert response.proposed_patch == patch

    with pytest.raises(ValidationError, match="must be set together"):
        AIInvokeResponse.model_validate(
            {
                **base,
                "proposed_patch": patch,
                "requires_confirmation": False,
            }
        )

    unpersisted_patch = patch.model_copy(update={"patch_id": None})
    with pytest.raises(ValidationError, match="persisted patch_id"):
        AIInvokeResponse.model_validate(
            {
                **base,
                "proposed_patch": unpersisted_patch,
                "requires_confirmation": True,
            }
        )


def test_response_collection_defaults_are_not_shared() -> None:
    common = {
        "request_id": uuid4(),
        "conversation_id": uuid4(),
        "route": InternalRoute.ALFRED,
        "message": "Vamos começar por um passo pequeno.",
        "usage": build_usage(),
    }
    first = AIInvokeResponse.model_validate(common)
    second = AIInvokeResponse.model_validate(common)

    first.references.append(
        EvidenceReference(
            document_id="doc-1",
            chunk_id="chunk-1",
            title="Reference",
            source="internal",
            retrieval_score=0.8,
            rerank_score=0.9,
        )
    )
    assert second.references == []


def test_agent_state_has_only_five_required_graph_inputs() -> None:
    assert AgentState.__required_keys__ == {
        "request_id",
        "user_id",
        "conversation_id",
        "selected_skill",
        "original_input",
    }
    assert "route" in AgentState.__optional_keys__
    assert "evidence_pack" in AgentState.__optional_keys__


def test_agent_state_excludes_runtime_dependencies_and_secrets() -> None:
    forbidden = {
        "password",
        "jwt",
        "database_session",
        "model_client",
        "stripe_client",
        "redis_connection",
        "plan_config",
        "openai_api_key",
    }
    assert forbidden.isdisjoint(AgentState.__annotations__)


def test_agent_state_is_accepted_by_langgraph_without_api_keys() -> None:
    graph_builder = StateGraph(AgentState)
    assert graph_builder.state_schema is AgentState


def test_legacy_graph_path_reexports_the_canonical_state() -> None:
    from graph.main import AgentState as LegacyAgentState

    assert LegacyAgentState is AgentState


def test_legacy_schema_modules_do_not_expose_separate_public_requests() -> None:
    import Alfred.schemas as alfred_schemas
    import feedbacker.schemas as feedbacker_schemas

    assert not hasattr(alfred_schemas, "AlfredRequest")
    assert not hasattr(feedbacker_schemas, "FeedbackerRequest")
