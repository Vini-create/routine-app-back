"""Alfred conversational capability with one bounded model call."""

from typing import Any

from langgraph.runtime import Runtime

from app.ai.domain.errors import AIApplicationError
from app.ai.graph.nodes._model import model_failure_update, model_usage_update
from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.models.gateway import ModelRole
from app.ai.prompts.alfred import build_alfred_system_prompt
from app.ai.prompts.payloads import bounded_json
from app.ai.schemas.alfred import AlfredIntervention


async def select_alfred_strategy_node(state: AgentState) -> dict[str, Any]:
    dropout_level = state.get("dropout_risk", {}).get("level")
    if state.get("evidence_pack"):
        strategy = "evidence_based_guidance"
    elif dropout_level == "high":
        strategy = "recovery_and_reduction"
    elif state.get("detected_intent") == "general_conversation":
        strategy = "supportive_clarification"
    else:
        strategy = "practical_next_step"
    return traced_update(
        state,
        "selecionar_estrategia_alfred",
        alfred_strategy=state.get("alfred_strategy", strategy),
    )


async def plan_alfred_response_node(state: AgentState) -> dict[str, Any]:
    risk = state.get("dropout_risk", {})
    anomalies = state.get("detected_anomalies", [])
    return traced_update(
        state,
        "planejar_resposta_alfred",
        alfred_plan=state.get(
            "alfred_plan",
            {
                "objective": "Help the user choose one realistic next action.",
                "tone": "warm_collaborative_practical",
                "key_points": [
                    f"dropout_risk={risk.get('level', 'unknown')}",
                    f"anomaly_count={len(anomalies)}",
                ],
                "next_steps": ["prioritize_the_smallest_useful_intervention"],
                "should_ask_question": not bool(state.get("habits")),
            },
        ),
    )


async def generate_alfred_intervention_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    gateway = (
        runtime.context.model_gateway
        if runtime is not None and runtime.context is not None
        else None
    )
    if gateway is not None:
        try:
            result = await gateway.invoke_structured(
                role=ModelRole.ALFRED,
                schema=AlfredIntervention,
                system_prompt=build_alfred_system_prompt(
                    state.get("response_language", "en")
                ),
                user_prompt=bounded_json(
                    {
                        "USER_INPUT": state["original_input"],
                        "selected_strategy": state.get("alfred_strategy"),
                        "response_plan": state.get("alfred_plan", {}),
                        "behavioral_state": state.get("behavioral_state", {}),
                        "goals": state.get("goals", [])[:10],
                        "habits": state.get("habits", [])[:20],
                        "evidence_pack": state.get("evidence_pack", {}),
                        "UNTRUSTED_CONTEXT": {
                            "recent_messages": state.get("recent_messages", [])[-8:],
                            "memories": state.get("relevant_memories", [])[:10],
                            "conversation_summary_en": state.get(
                                "conversation_summary",
                                "",
                            ),
                        },
                    }
                ),
            )
            return traced_update(
                state,
                "gerar_intervencao_alfred",
                alfred_intervention=result.parsed.model_dump(mode="json"),
                summary_update=result.parsed.updated_summary_en,
                token_usage=model_usage_update(state, result, ModelRole.ALFRED),
            )
        except AIApplicationError as error:
            return traced_update(
                state,
                "gerar_intervencao_alfred",
                alfred_intervention={
                    "strategy": state.get(
                        "alfred_strategy",
                        "supportive_guidance",
                    ),
                    "message": _fallback_message(state.get("response_language", "en")),
                    "next_steps": [],
                    "memory_candidates": [],
                },
                **model_failure_update(
                    state,
                    error,
                    component="alfred_model",
                    fallback="localized_alfred_fallback",
                ),
            )

    return traced_update(
        state,
        "gerar_intervencao_alfred",
        alfred_intervention=state.get(
            "alfred_intervention",
            {
                "strategy": state.get(
                    "alfred_strategy",
                    "supportive_guidance",
                ),
                "message": "Intervenção conversacional de teste.",
                "next_steps": [],
                "memory_candidates": [],
            },
        ),
    )


async def render_alfred_response_node(state: AgentState) -> dict[str, Any]:
    intervention = state.get("alfred_intervention", {})
    extracted_memories = [
        {
            "value": candidate,
            "source": "alfred_intervention",
            "confidence": 0.6,
        }
        for candidate in intervention.get("memory_candidates", [])
        if isinstance(candidate, str)
    ]
    return traced_update(
        state,
        "renderizar_resposta_alfred",
        rendered_response=state.get(
            "rendered_response",
            str(intervention.get("message", "Resposta do Alfred de teste.")),
        ),
        memory_candidates=[
            *state.get("memory_candidates", []),
            *extracted_memories,
        ],
    )


def _fallback_message(language: str) -> str:
    return {
        "pt-BR": (
            "Não consegui concluir a orientação agora. Seus dados continuam "
            "seguros; tente novamente em alguns instantes."
        ),
        "es": (
            "No pude completar la orientación ahora. Tus datos siguen seguros; "
            "inténtalo de nuevo en unos instantes."
        ),
        "fr": (
            "Je n’ai pas pu terminer l’orientation maintenant. Vos données "
            "restent protégées ; réessayez dans quelques instants."
        ),
        "en": (
            "I could not complete the guidance right now. Your data remains safe; "
            "please try again in a moment."
        ),
    }.get(language, "I could not complete the guidance right now.")
