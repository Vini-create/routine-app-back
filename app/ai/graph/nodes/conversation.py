"""Alfred conversation with a bounded model call and one optional rewrite."""

import re
import unicodedata
from difflib import SequenceMatcher
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
from app.ai.retrieval.editorial_phrases import retrieve_motivational_phrase
from app.ai.schemas.alfred import AlfredIntervention
from app.ai.services.routing_service import active_goals

_CONTEXT_FREE_STRATEGIES = {
    "social_greeting",
    "identity_and_scope",
    "context_transparency",
}
_EXPLICIT_REPETITION_REQUEST = re.compile(
    r"\b(?:repita|repete|diga de novo|novamente|repeat|say that again|"
    r"repite|repetez)\b"
)


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
    if re.search(
        r"\b(?:voce (?:tem|ve|sabe|acessa)|quais dados|que informacoes|"
        r"what data|what information|que datos|quelles donnees)\b",
        canonical,
    ) and re.search(
        r"\b(?:habitos?|rotina|metas?|dados|informacoes|habits?|routine|"
        r"goals?|data|datos|rutina|donnees|habitudes?)\b",
        canonical,
    ):
        return "context_transparency"
    return None


async def select_alfred_strategy_node(state: AgentState) -> dict[str, Any]:
    direct_strategy = _direct_conversation_strategy(state["original_input"])
    dropout_risk = state.get("dropout_risk", {})
    if state.get("detected_intent") == "routine_goal_clarification":
        strategy = "clarify_routine_goal"
    elif direct_strategy is not None:
        strategy = direct_strategy
    elif state.get("route") in {
        "rag_then_alfred",
        "rag_then_feedbacker",
    } or state.get("evidence_pack", {}).get("references"):
        strategy = "evidence_explanation"
    elif (
        dropout_risk.get("level") == "high"
        and float(dropout_risk.get("confidence", 0.0)) >= 0.5
    ):
        strategy = "recovery_support"
    else:
        strategy = "adaptive_conversation"
    editorial_phrase = retrieve_motivational_phrase(
        state["original_input"],
        response_language=state.get("response_language", "en"),
        recent_assistant_messages=_assistant_messages(state),
    )
    return traced_update(
        state,
        "selecionar_estrategia_alfred",
        alfred_strategy=state.get("alfred_strategy", strategy),
        editorial_phrase=state.get("editorial_phrase", editorial_phrase),
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
        "clarify_routine_goal": (
            "Before designing an ideal routine, ask one concise question to "
            "identify the user's current priority. If active_goals are supplied, "
            "mention their titles naturally and ask which one should guide the "
            "routine. Do not generate the routine in this turn."
        ),
        "evidence_explanation": (
            "Answer the evidence question directly. Synthesize the supported "
            "findings, material limitations, and relevance to the user's exact "
            "question. Practical advice is secondary and only included when asked."
        ),
        "recovery_support": (
            "Address the request while accounting for a high-confidence execution "
            "difficulty. Explain the relevant tradeoffs and offer options rather "
            "than automatically prescribing a smaller daily action."
        ),
        "adaptive_conversation": (
            "Resolve the current request at an appropriate depth. Choose whether "
            "the user needs an explanation, reflection, comparison, clarification, "
            "or plan; do not force the turn into coaching advice."
        ),
    }
    return traced_update(
        state,
        "planejar_resposta_alfred",
        alfred_plan=state.get(
            "alfred_plan",
            {
                "objective": objectives.get(
                    strategy, objectives["adaptive_conversation"]
                ),
                "tone": "warm_collaborative_practical",
                "key_points": [
                    f"selected_strategy={strategy}",
                    f"dropout_risk={risk.get('level', 'unknown')}",
                    f"anomaly_count={len(anomalies)}",
                ],
                "next_steps": [],
                "should_ask_question": strategy == "clarify_routine_goal",
            },
        ),
    )


def _assistant_messages(state: AgentState) -> list[str]:
    return [
        str(message.get("content", "")).strip()
        for message in state.get("recent_messages", [])[-8:]
        if message.get("role") == "assistant"
        and str(message.get("content", "")).strip()
    ][-3:]


def _normalized_words(value: str) -> set[str]:
    return {
        word
        for word in re.findall(r"\b[\w-]{4,}\b", _canonical(value))
        if word
        not in {
            "para",
            "como",
            "comecar",
            "voce",
            "essa",
            "isso",
            "pode",
            "your",
            "that",
            "this",
            "with",
            "from",
            "para",
            "esta",
        }
    }


def _repetition_score(candidate: str, previous: str) -> float:
    candidate_words = _normalized_words(candidate)
    previous_words = _normalized_words(previous)
    union = candidate_words | previous_words
    lexical_overlap = (
        len(candidate_words & previous_words) / len(union) if union else 0.0
    )
    sequence_overlap = SequenceMatcher(
        None,
        _canonical(candidate),
        _canonical(previous),
    ).ratio()
    return max(lexical_overlap, sequence_overlap)


def _repeats_recent_answer(state: AgentState, candidate: str) -> bool:
    if _EXPLICIT_REPETITION_REQUEST.search(_canonical(state["original_input"])):
        return False
    return any(
        _repetition_score(candidate, previous) >= 0.58
        for previous in _assistant_messages(state)
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
            current_goals = active_goals(list(state.get("goals", [])))
            ordered_goals = [
                *current_goals,
                *[goal for goal in state.get("goals", []) if goal not in current_goals],
            ][:10]
            user_payload = {
                "USER_INPUT": state["original_input"],
                "selected_strategy": strategy,
                "response_plan": state.get("alfred_plan", {}),
                "context_inventory": context_inventory,
                "behavioral_state": (
                    state.get("behavioral_state", {}) if use_routine_context else {}
                ),
                "active_goals": current_goals[:10] if use_routine_context else [],
                "goals": ordered_goals if use_routine_context else [],
                "habits": (state.get("habits", [])[:20] if use_routine_context else []),
                "evidence_pack": (
                    state.get("evidence_pack", {}) if use_routine_context else {}
                ),
                "editorial_phrase": (
                    state.get("editorial_phrase") if use_routine_context else None
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
            result = await gateway.invoke_structured(
                role=ModelRole.ALFRED,
                schema=AlfredIntervention,
                system_prompt=build_alfred_system_prompt(
                    state.get("response_language", "en")
                ),
                user_prompt=bounded_json(user_payload),
            )
            token_usage = model_usage_update(state, result, ModelRole.ALFRED)
            if _repeats_recent_answer(state, result.parsed.message):
                revision_state = AgentState(**state)
                revision_state["token_usage"] = token_usage
                result = await gateway.invoke_structured(
                    role=ModelRole.ALFRED,
                    schema=AlfredIntervention,
                    system_prompt=build_alfred_system_prompt(
                        state.get("response_language", "en")
                    ),
                    user_prompt=bounded_json(
                        {
                            **user_payload,
                            "REVISION_REQUIRED": {
                                "reason": (
                                    "The draft substantially repeats a recent "
                                    "Alfred answer."
                                ),
                                "draft": result.parsed.message,
                                "required_change": (
                                    "Answer from a materially different and deeper "
                                    "angle. Add useful information, distinctions, "
                                    "or a focused question; do not paraphrase the "
                                    "same recommendation."
                                ),
                            },
                        }
                    ),
                )
                token_usage = model_usage_update(
                    revision_state,
                    result,
                    ModelRole.ALFRED,
                )
            return traced_update(
                state,
                "gerar_intervencao_alfred",
                alfred_intervention=result.parsed.model_dump(mode="json"),
                summary_update=result.parsed.updated_summary_en,
                token_usage=token_usage,
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
