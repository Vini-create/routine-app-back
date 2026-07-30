"""Model-role integration tests using fake adapters and no paid API calls."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel

from app.ai.domain.enums import InternalRoute, SelectedSkill
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.graph import (
    GRAPH_RECURSION_LIMIT,
    GraphRuntimeContext,
    build_graph,
)
from app.ai.graph.state import AgentState
from app.ai.models.gateway import (
    LangChainOpenAIModelGateway,
    ModelInvocationResult,
    ModelRole,
    ModelSpec,
    SchemaT,
    build_default_model_gateway,
)
from app.ai.schemas.alfred import AlfredIntervention
from app.ai.schemas.analysis import (
    AnalysisSynthesis,
    ModelPatchProposal,
    Recommendation,
    RootCauseHypothesis,
    SuccessMetric,
)
from app.ai.schemas.patches import PatchOperation, ProposedPatch
from app.ai.schemas.routing import RoutingDecision
from app.ai.schemas.critic import CriticReview


@pytest.mark.parametrize(
    "invalid_options",
    [
        {"temperature": 2.1},
        {"max_tokens": 0},
        {"top_p": 1.1},
        {"frequency_penalty": -2.1},
        {"presence_penalty": 2.1},
    ],
)
def test_model_spec_rejects_invalid_inference_parameters(
    invalid_options: dict[str, Any],
) -> None:
    with pytest.raises(ValueError):
        ModelSpec(
            model="gpt-4o-mini",
            use_responses_api=False,
            **invalid_options,
        )


def test_responses_api_rejects_unsupported_penalty_parameters() -> None:
    with pytest.raises(ValueError, match="not supported"):
        ModelSpec(
            model="gpt-5",
            use_responses_api=True,
            presence_penalty=0.0,
        )


def test_feedbacker_schema_is_strict_and_backend_enriches_the_patch() -> None:
    schema = AnalysisSynthesis.model_json_schema()
    serialized_schema = str(schema)

    assert "'additionalProperties': True" not in serialized_schema
    model_patch_schema = schema["$defs"]["ModelPatchProposal"]["properties"]
    assert "patch_id" not in model_patch_schema
    assert "simulation" not in model_patch_schema

    draft = ModelPatchProposal(
        entity_type="routine_item",
        entity_id=None,
        operations=[
            PatchOperation(
                op="replace",
                path="/duration_minutes",
                value=30,
            )
        ],
        reason="Synthetic model proposal.",
        success_metrics=[
            SuccessMetric(
                name="Completion rate",
                target="increase",
                evaluation_window_days=14,
            )
        ],
    )
    backend_patch = ProposedPatch.model_validate(draft.model_dump(mode="json"))

    assert backend_patch.patch_id is None
    assert backend_patch.simulation is None
    assert backend_patch.success_metrics[0]["name"] == "Completion rate"


def test_gateway_only_sends_parameters_supported_by_each_model_role() -> None:
    created_clients: list[dict[str, Any]] = []

    def capture_client(**kwargs: Any) -> Mock:
        created_clients.append(kwargs)
        return Mock()

    gateway = LangChainOpenAIModelGateway(
        api_key="test-key",
        specs={
            ModelRole.ROUTER: ModelSpec(
                model="gpt-4o-mini",
                use_responses_api=False,
                temperature=0.0,
                max_tokens=400,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            ),
            ModelRole.ALFRED: ModelSpec(
                model="gpt-4o-mini",
                use_responses_api=False,
                temperature=0.3,
                max_tokens=1_300,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            ),
            ModelRole.FEEDBACKER: ModelSpec(
                model="gpt-5",
                use_responses_api=True,
                max_tokens=3_600,
                reasoning_effort="medium",
                verbosity="medium",
            ),
            ModelRole.CRITIC: ModelSpec(
                model="gpt-4o-mini",
                use_responses_api=False,
                temperature=0.0,
                max_tokens=800,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            ),
        },
        timeout_seconds=45.0,
        max_retries=2,
    )

    with patch("app.ai.models.gateway.ChatOpenAI", side_effect=capture_client):
        gateway._client(ModelRole.ROUTER)
        gateway._client(ModelRole.ALFRED)
        gateway._client(ModelRole.FEEDBACKER)
        gateway._client(ModelRole.CRITIC)

    by_model_role = dict(zip(ModelRole, created_clients, strict=True))
    for role in (ModelRole.ROUTER, ModelRole.CRITIC):
        assert by_model_role[role]["model"] == "gpt-4o-mini"
        assert by_model_role[role]["use_responses_api"] is False
        assert by_model_role[role]["top_p"] == 1.0
        assert by_model_role[role]["frequency_penalty"] == 0.0
        assert by_model_role[role]["presence_penalty"] == 0.0
        assert "reasoning_effort" not in by_model_role[role]
        assert "verbosity" not in by_model_role[role]

    assert by_model_role[ModelRole.ROUTER]["temperature"] == 0.0
    assert by_model_role[ModelRole.ROUTER]["max_tokens"] == 400
    assert by_model_role[ModelRole.ALFRED]["model"] == "gpt-4o-mini"
    assert by_model_role[ModelRole.ALFRED]["use_responses_api"] is False
    assert by_model_role[ModelRole.ALFRED]["temperature"] == 0.3
    assert by_model_role[ModelRole.ALFRED]["max_tokens"] == 1_300
    assert by_model_role[ModelRole.ALFRED]["top_p"] == 1.0
    assert by_model_role[ModelRole.ALFRED]["frequency_penalty"] == 0.0
    assert by_model_role[ModelRole.ALFRED]["presence_penalty"] == 0.0
    assert "reasoning_effort" not in by_model_role[ModelRole.ALFRED]
    assert "verbosity" not in by_model_role[ModelRole.ALFRED]
    assert by_model_role[ModelRole.CRITIC]["temperature"] == 0.0
    assert by_model_role[ModelRole.CRITIC]["max_tokens"] == 800

    assert by_model_role[ModelRole.FEEDBACKER]["model"] == "gpt-5"
    assert by_model_role[ModelRole.FEEDBACKER]["use_responses_api"] is True
    assert by_model_role[ModelRole.FEEDBACKER]["max_tokens"] == 3_600
    assert by_model_role[ModelRole.FEEDBACKER]["reasoning_effort"] == "medium"
    assert by_model_role[ModelRole.FEEDBACKER]["verbosity"] == "medium"
    for unsupported_parameter in (
        "temperature",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
    ):
        assert unsupported_parameter not in by_model_role[ModelRole.FEEDBACKER]


def test_default_alfred_model_uses_the_cost_efficient_conversational_tier() -> None:
    gateway = build_default_model_gateway()
    spec = gateway._specs[ModelRole.ALFRED]

    assert spec.model == "gpt-4o-mini"
    assert spec.use_responses_api is False
    assert spec.temperature == 0.3
    assert spec.max_tokens == 1_300


class FakeModelGateway:
    def __init__(
        self,
        *,
        fail_role: ModelRole | None = None,
        alfred_messages: list[str] | None = None,
    ) -> None:
        self.calls: list[ModelRole] = []
        self.user_prompts: list[tuple[ModelRole, str]] = []
        self.fail_role = fail_role
        self.alfred_messages = alfred_messages or [
            (
                "Antes de escolher uma ação, vale distinguir se o obstáculo é "
                "carga excessiva, prioridade incerta ou falta de energia; cada "
                "causa pede uma resposta diferente."
            )
        ]
        self.alfred_call_count = 0

    async def invoke_structured(
        self,
        *,
        role: ModelRole,
        schema: type[SchemaT],
        system_prompt: str,
        user_prompt: str,
    ) -> ModelInvocationResult[SchemaT]:
        self.calls.append(role)
        self.user_prompts.append((role, user_prompt))
        assert "Security and authority" in system_prompt
        assert "USER_INPUT" in user_prompt
        if self.fail_role is not None and role is self.fail_role:
            raise AIApplicationError(
                AIErrorCode.MODEL_UNAVAILABLE,
                f"{role.value} unavailable in test",
            )

        output: BaseModel
        if role is ModelRole.ROUTER:
            output = RoutingDecision(
                detected_intent="needs_support",
                intent_confidence=0.9,
                route=InternalRoute.ALFRED,
                route_confidence=0.88,
                route_reason="Ambiguous request resolved as conversation.",
            )
        elif role is ModelRole.ALFRED:
            message = self.alfred_messages[
                min(self.alfred_call_count, len(self.alfred_messages) - 1)
            ]
            self.alfred_call_count += 1
            output = AlfredIntervention(
                strategy="adaptive_conversation",
                message=message,
                next_steps=[],
                memory_candidates=[],
                updated_summary_en=(
                    "The user is exploring which barrier is affecting execution."
                ),
            )
        elif role is ModelRole.FEEDBACKER:
            output = AnalysisSynthesis(
                hypotheses=[
                    RootCauseHypothesis(
                        hypothesis="A carga planejada pode estar alta.",
                        supporting_evidence=["A conclusão recente caiu."],
                        confidence=0.7,
                    )
                ],
                recommendations=[
                    Recommendation(
                        priority=1,
                        title="Reduzir a carga",
                        rationale="A queda coincide com a carga planejada.",
                        action="Reduzir temporariamente uma ocorrência semanal.",
                    )
                ],
                success_metrics=[
                    SuccessMetric(
                        name="Taxa de conclusão",
                        baseline="current",
                        target="increase by 10 percentage points",
                        evaluation_window_days=14,
                    )
                ],
                response_message="Alfred encontrou uma possível sobrecarga.",
                updated_summary_en=(
                    "The user may be overloaded and is reviewing routine load."
                ),
            )
        elif role is ModelRole.CRITIC:
            output = CriticReview(approved=True)
        else:
            raise AssertionError(f"Unexpected role: {role}")

        return ModelInvocationResult(
            parsed=output,  # type: ignore[arg-type]
            model=f"fake-{role.value}",
            usage={
                "input_tokens": 100,
                "output_tokens": 25,
                "total_tokens": 125,
            },
        )


def state(message: str) -> AgentState:
    return AgentState(
        request_id="00000000-0000-0000-0000-000000000001",
        user_id="00000000-0000-0000-0000-000000000002",
        conversation_id=None,
        selected_skill=SelectedSkill.AUTO,
        original_input=message,
    )


async def invoke(
    request_state: AgentState,
    gateway: FakeModelGateway,
) -> dict[str, Any]:
    return dict(
        await build_graph().ainvoke(
            request_state,
            {"recursion_limit": GRAPH_RECURSION_LIMIT},
            context=GraphRuntimeContext(model_gateway=gateway),
        )
    )


@pytest.mark.asyncio
async def test_ambiguous_request_uses_router_then_alfred_only() -> None:
    gateway = FakeModelGateway()
    result = await invoke(state("Preciso de ajuda com esta semana."), gateway)

    assert gateway.calls == [ModelRole.ROUTER, ModelRole.ALFRED]
    assert result["route"] is InternalRoute.ALFRED
    assert result["alfred_strategy"] == "adaptive_conversation"
    assert result["alfred_plan"]["next_steps"] == []
    assert "smallest" not in result["alfred_plan"]["objective"]
    assert result["rendered_response"].startswith("Antes de escolher")
    assert result["token_usage"]["model_calls"] == 2
    assert result["token_usage"]["total_tokens"] == 250
    assert result["summary_update"].startswith("The user is exploring")
    assert result["final_response"]["translation_applied"] is False


@pytest.mark.asyncio
async def test_repetitive_alfred_draft_is_rewritten_once() -> None:
    repeated = "Escolha uma tarefa pequena e faça por dez minutos hoje."
    gateway = FakeModelGateway(
        alfred_messages=[
            repeated,
            (
                "A procrastinação pode vir de aversão à tarefa, recompensa "
                "distante ou critérios pouco claros. Identificar qual desses "
                "mecanismos aparece no episódio muda a estratégia adequada."
            ),
        ]
    )
    request_state = state("O que mais pode explicar essa procrastinação?")
    request_state["recent_messages"] = [
        {"role": "assistant", "content": repeated},
    ]

    result = await invoke(request_state, gateway)

    assert gateway.calls == [
        ModelRole.ROUTER,
        ModelRole.ALFRED,
        ModelRole.ALFRED,
    ]
    assert "REVISION_REQUIRED" in gateway.user_prompts[-1][1]
    assert result["rendered_response"].startswith("A procrastinação pode")
    assert result["token_usage"]["model_calls"] == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("message", "expected_strategy"),
    [
        ("Olá!", "social_greeting"),
        ("Quem é você?", "identity_and_scope"),
        (
            "Você tem informações sobre meus hábitos aí?",
            "context_transparency",
        ),
    ],
)
async def test_direct_conversation_never_becomes_unrelated_routine_advice(
    message: str,
    expected_strategy: str,
) -> None:
    gateway = FakeModelGateway()
    request_state = state(message)
    request_state["habits"] = [
        {
            "id": "habit-1",
            "name": "Dormir cedo",
            "status": "active",
        }
    ]
    request_state["recent_messages"] = [
        {
            "role": "assistant",
            "content": "Tente dormir oito horas.",
        }
    ]

    result = await invoke(request_state, gateway)

    assert result["alfred_strategy"] == expected_strategy
    alfred_prompt = next(
        prompt
        for role, prompt in gateway.user_prompts
        if role is ModelRole.ALFRED
    )
    assert f'"selected_strategy":"{expected_strategy}"' in alfred_prompt
    assert '"behavioral_state":{}' in alfred_prompt
    assert '"habits":[]' in alfred_prompt
    assert "Tente dormir oito horas." not in alfred_prompt
    if expected_strategy == "context_transparency":
        assert (
            '"context_inventory":{"goals":0,"habits":1,'
            '"routine_items":0,"recent_messages":1}'
        ) in alfred_prompt


@pytest.mark.asyncio
async def test_obvious_deterministic_request_never_calls_a_model() -> None:
    gateway = FakeModelGateway()
    result = await invoke(state("Quantos hábitos ativos eu tenho?"), gateway)

    assert gateway.calls == []
    assert result["route"] is InternalRoute.DETERMINISTIC
    assert result["token_usage"] == {}
    assert "hábito(s) ativo(s)" in result["rendered_response"]


@pytest.mark.asyncio
async def test_obvious_deep_analysis_uses_feedbacker_and_critic_models() -> None:
    gateway = FakeModelGateway()
    result = await invoke(
        state("Analise profundamente meus últimos 30 dias de rotina."),
        gateway,
    )

    assert gateway.calls == [ModelRole.FEEDBACKER, ModelRole.CRITIC]
    assert result["route"] is InternalRoute.FEEDBACKER
    assert result["root_cause_hypotheses"][0]["confidence"] == 0.7
    assert result["recommendations"][0]["title"] == "Reduzir a carga"
    assert result["success_metrics"][0]["evaluation_window_days"] == 14
    assert result["proposed_patch"] is None
    assert result["summary_update"].startswith("The user may be overloaded")
    assert result["analysis_report"]["metadata"]["patch_generation_enabled"] is True


@pytest.mark.asyncio
async def test_decision_memory_is_sent_only_to_feedbacker() -> None:
    decision_memory = {
        "type": "routine_item:start_at",
        "context": "Move study time earlier.",
        "decision": "rejected",
        "reason": "I cannot study before 08:00.",
        "inferred_preference": "Avoid early study suggestions.",
        "confidence": 0.85,
    }
    alfred_state = state("Preciso de ajuda com esta semana.")
    alfred_state["conversation_summary"] = "The user is planning the week."
    alfred_state["feedbacker_decision_memories"] = [decision_memory]
    alfred_gateway = FakeModelGateway()

    await invoke(alfred_state, alfred_gateway)

    alfred_prompt = next(
        prompt
        for role, prompt in alfred_gateway.user_prompts
        if role is ModelRole.ALFRED
    )
    assert "The user is planning the week." in alfred_prompt
    assert "feedbacker_decision_memories" not in alfred_prompt
    assert "I cannot study before 08:00." not in alfred_prompt

    feedbacker_state = state(
        "Analise profundamente meus últimos 30 dias de rotina."
    )
    feedbacker_state["conversation_summary"] = "The user is reviewing consistency."
    feedbacker_state["feedbacker_decision_memories"] = [decision_memory]
    feedbacker_gateway = FakeModelGateway()

    await invoke(feedbacker_state, feedbacker_gateway)

    feedbacker_prompt = next(
        prompt
        for role, prompt in feedbacker_gateway.user_prompts
        if role is ModelRole.FEEDBACKER
    )
    assert "The user is reviewing consistency." in feedbacker_prompt
    assert "feedbacker_decision_memories" in feedbacker_prompt
    assert "I cannot study before 08:00." in feedbacker_prompt


@pytest.mark.asyncio
async def test_model_failure_is_explicit_and_uses_localized_fallback() -> None:
    gateway = FakeModelGateway(fail_role=ModelRole.ALFRED)
    result = await invoke(state("Preciso de ajuda com esta semana."), gateway)

    assert gateway.calls == [ModelRole.ROUTER, ModelRole.ALFRED]
    assert result["degraded_mode"] is True
    assert result["fallback_used"] == "localized_alfred_fallback"
    assert "alfred_model" in result["unavailable_components"]
    assert result["errors"][-1]["code"] == AIErrorCode.MODEL_UNAVAILABLE.value
    assert result["token_usage"]["model_calls"] == 1
