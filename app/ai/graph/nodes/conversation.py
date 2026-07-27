"""Alfred conversational capability with one bounded model call."""

import re
import unicodedata
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

_CONTEXT_FREE_STRATEGIES = {
    "social_greeting",
    "identity_and_scope",
    "context_transparency",
}


def _canonical(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(
        character for character in folded if not unicodedata.combining(character)
    )
    return " ".join(without_accents.split())


def _direct_conversation_strategy(message: str) -> str | None:
    canonical = _canonical(message).strip(" .,!?:;")
    if re.fullmatch(
        r"(?:oi|ola|e ai|bom dia|boa tarde|boa noite|hello|hi|hey|hola|"
        r"buenos dias|bonjour|salut)",
        canonical,
    ):
        return "social_greeting"
    if re.search(
        r"\b(?:quem e voce|o que voce e|se apresente|what are you|who are you|"
        r"quien eres|qui es tu|presente-toi)\b",
        canonical,
    ):
        return "identity_and_scope"
    if (
        re.search(
            r"\b(?:voce (?:tem|ve|sabe|acessa)|quais dados|que informacoes|"
            r"what data|what information|que datos|quelles donnees)\b",
            canonical,
        )
        and re.search(
            r"\b(?:habitos?|rotina|metas?|dados|informacoes|habits?|routine|"
            r"goals?|data|datos|rutina|donnees|habitudes?)\b",
            canonical,
        )
    ):
        return "context_transparency"
    return None


async def select_alfred_strategy_node(state: AgentState) -> dict[str, Any]:
    direct_strategy = _direct_conversation_strategy(state["original_input"])
    dropout_level = state.get("dropout_risk", {}).get("level")
    if direct_strategy is not None:
        strategy = direct_strategy
    elif state.get("evidence_pack"):
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
    strategy = state.get("alfred_strategy", "practical_next_step")
    objectives = {
        "social_greeting": (
            "Reply naturally to the greeting and briefly invite the user to "
            "share what they need."
        ),
        "identity_and_scope": (
            "Explain who Alfred is and what Alfred can help with, without "
            "inventing access or giving unsolicited routine advice."
        ),
        "context_transparency": (
            "Answer transparently which application data categories are "
            "available in this request, using context_inventory only."
        ),
    }
    return traced_update(
        state,
        "planejar_resposta_alfred",
        alfred_plan=state.get(
            "alfred_plan",
            {
                "objective": objectives.get(
                    strategy,
                    "Help the user choose one realistic next action.",
                ),
                "tone": "warm_collaborative_practical",
                "key_points": [
                    f"selected_strategy={strategy}",
                    f"dropout_risk={risk.get('level', 'unknown')}",
                    f"anomaly_count={len(anomalies)}",
                ],
                "next_steps": (
                    []
                    if strategy in _CONTEXT_FREE_STRATEGIES
                    else ["prioritize_the_smallest_useful_intervention"]
                ),
                "should_ask_question": (
                    False
                    if strategy in _CONTEXT_FREE_STRATEGIES
                    else not bool(state.get("habits"))
                ),
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
            strategy = state.get("alfred_strategy", "practical_next_step")
            use_routine_context = strategy not in _CONTEXT_FREE_STRATEGIES
            context_inventory = (
                {
                    "goals": len(state.get("goals", [])),
                    "habits": len(state.get("habits", [])),
                    "routine_items": len(state.get("routines", [])),
                    "recent_messages": len(state.get("recent_messages", [])),
                }
                if strategy == "context_transparency"
                else {}
            )
            result = await gateway.invoke_structured(
                role=ModelRole.ALFRED,
                schema=AlfredIntervention,
                system_prompt=build_alfred_system_prompt(
                    state.get("response_language", "en")
                ),
                user_prompt=bounded_json(
                    {
                        "USER_INPUT": state["original_input"],
                        "selected_strategy": strategy,
                        "response_plan": state.get("alfred_plan", {}),
                        "context_inventory": context_inventory,
                        "behavioral_state": (
                            state.get("behavioral_state", {})
                            if use_routine_context
                            else {}
                        ),
                        "goals": (
                            state.get("goals", [])[:10]
                            if use_routine_context
                            else []
                        ),
                        "habits": (
                            state.get("habits", [])[:20]
                            if use_routine_context
                            else []
                        ),
                        "evidence_pack": (
                            state.get("evidence_pack", {})
                            if use_routine_context
                            else {}
                        ),
                        "UNTRUSTED_CONTEXT": {
                            "recent_messages": (
                                state.get("recent_messages", [])[-8:]
                                if use_routine_context
                                else []
                            ),
                            "memories": (
                                state.get("relevant_memories", [])[:10]
                                if use_routine_context
                                else []
                            ),
                            "conversation_summary_en": (
                                state.get("conversation_summary", "")
                                if use_routine_context
                                else ""
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
