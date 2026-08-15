"""Alfred's internal deep analysis with one evidence-bounded model call."""

from typing import Any

from langgraph.runtime import Runtime

from app.ai.domain.errors import AIApplicationError
from app.ai.graph.nodes._model import model_failure_update, model_usage_update
from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.models.gateway import ModelRole
from app.ai.prompts.analysis import build_feedbacker_system_prompt
from app.ai.prompts.payloads import bounded_json
from app.ai.schemas.analysis import AnalysisSynthesis
from app.ai.services.routing_service import (
    active_goals,
    is_explicit_patch_request,
    is_open_ended_patch_request,
)


def _analysis_language(state: AgentState) -> str:
    return str(state.get("response_language", "en"))


def _execution_diagnosis(
    *,
    language: str,
    expected: int,
    completed: int,
    completion_rate: Any,
    window: dict[str, Any],
    trend_count: int,
    anomaly_count: int,
) -> dict[str, Any]:
    templates = {
        "pt-BR": {
            "summary": "{completed} de {expected} ocorrências programadas foram concluídas no período analisado.",
            "expected": "ocorrências_planejadas={value}",
            "completed": "ocorrências_concluídas={value}",
            "rate": "taxa_de_conclusão={value}",
            "trends": "tendências_detectadas={value}",
            "anomalies": "anomalias_detectadas={value}",
        },
        "es": {
            "summary": "Se completaron {completed} de {expected} ocurrencias programadas en el período analizado.",
            "expected": "ocurrencias_programadas={value}",
            "completed": "ocurrencias_completadas={value}",
            "rate": "tasa_de_finalización={value}",
            "trends": "tendencias_detectadas={value}",
            "anomalies": "anomalías_detectadas={value}",
        },
        "fr": {
            "summary": "{completed} occurrences planifiées sur {expected} ont été réalisées pendant la période analysée.",
            "expected": "occurrences_planifiées={value}",
            "completed": "occurrences_réalisées={value}",
            "rate": "taux_de_réalisation={value}",
            "trends": "tendances_détectées={value}",
            "anomalies": "anomalies_détectées={value}",
        },
        "en": {
            "summary": "{completed} of {expected} scheduled occurrences were completed in the analyzed window.",
            "expected": "scheduled_occurrences={value}",
            "completed": "completed_occurrences={value}",
            "rate": "completion_rate={value}",
            "trends": "detected_trends={value}",
            "anomalies": "detected_anomalies={value}",
        },
    }
    labels = templates.get(language, templates["en"])
    return {
        "summary": str(labels["summary"]).format(
            completed=completed,
            expected=expected,
        ),
        "data_window": (
            f"{window.get('start_date', 'unknown')}.."
            f"{window.get('end_date', 'unknown')}"
        ),
        "data_quality": min(1.0, expected / 20),
        "observed_facts": [
            str(labels["expected"]).format(value=expected),
            str(labels["completed"]).format(value=completed),
            str(labels["rate"]).format(value=completion_rate),
            str(labels["trends"]).format(value=trend_count),
            str(labels["anomalies"]).format(value=anomaly_count),
        ],
    }


async def diagnose_execution_node(state: AgentState) -> dict[str, Any]:
    metrics = state.get("habit_metrics", {})
    summary = metrics.get("summary", {})
    expected = int(summary.get("expected_count", 0))
    completed = int(summary.get("completed_count", 0))
    rate = summary.get("completion_rate")
    window = metrics.get("window", {})
    diagnosis = _execution_diagnosis(
        language=_analysis_language(state),
        expected=expected,
        completed=completed,
        completion_rate=rate,
        window=window,
        trend_count=len(state.get("detected_trends", [])),
        anomaly_count=len(state.get("detected_anomalies", [])),
    )
    return traced_update(
        state,
        "diagnosticar_execucao",
        execution_diagnosis=state.get(
            "execution_diagnosis",
            diagnosis,
        ),
    )


async def identify_patterns_node(state: AgentState) -> dict[str, Any]:
    patterns: list[dict[str, Any]] = []
    for trend in state.get("detected_trends", []):
        if trend.get("type") == "insufficient_history":
            continue
        patterns.append(
            {
                "name": f"trend:{trend.get('type', 'unknown')}",
                "description": (
                    f"Direction={trend.get('direction', 'unknown')}; "
                    f"delta={trend.get('delta', 'not_available')}."
                ),
                "evidence": [bounded_json(trend, max_chars=1_000)],
                "confidence": float(trend.get("confidence", 0.5)),
            }
        )
    for anomaly in state.get("detected_anomalies", []):
        patterns.append(
            {
                "name": f"anomaly:{anomaly.get('type', 'unknown')}",
                "description": (
                    f"Transparent rule detected severity "
                    f"{anomaly.get('severity', 'unknown')}."
                ),
                "evidence": [
                    bounded_json(anomaly.get("evidence", {}), max_chars=1_000)
                ],
                "confidence": 0.8,
            }
        )
    return traced_update(
        state,
        "identificar_padroes",
        identified_patterns=list(state.get("identified_patterns", patterns)),
    )


async def generate_hypotheses_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    # An open-ended request such as "make this fit my time" does not need an
    # expensive model call when the trusted context already contains a safe,
    # owned duration candidate.  Keeping this path deterministic makes the
    # confirmation feature fast and available even if the Feedbacker model is
    # temporarily slow or unavailable.
    if is_open_ended_patch_request(state["original_input"]):
        deterministic_patch = _conservative_duration_patch(state)
        if deterministic_patch is not None:
            return traced_update(
                state,
                "gerar_hipoteses",
                root_cause_hypotheses=[],
                analysis_model_output={
                    "hypotheses": [],
                    "recommendations": [],
                    "success_metrics": deterministic_patch["success_metrics"],
                    "response_message": _deterministic_patch_response(
                        language=_analysis_language(state),
                        reason=str(deterministic_patch["reason"]),
                    ),
                    "proposed_patch": deterministic_patch,
                },
            )

    gateway = (
        runtime.context.model_gateway
        if runtime is not None and runtime.context is not None
        else None
    )
    if gateway is not None:
        try:
            result = await gateway.invoke_structured(
                role=ModelRole.FEEDBACKER,
                schema=AnalysisSynthesis,
                system_prompt=build_feedbacker_system_prompt(
                    state.get("response_language", "en")
                ),
                user_prompt=bounded_json(
                    {
                        "USER_INPUT": state["original_input"],
                        "selected_skill": state["selected_skill"].value,
                        "patch_request": {
                            "explicit": is_explicit_patch_request(
                                state["original_input"]
                            ),
                            "open_ended_suggestion": is_open_ended_patch_request(
                                state["original_input"]
                            ),
                            "instruction": (
                                "Propose one validated change when the target and "
                                "new value are unambiguous; otherwise ask one question."
                            ),
                            "editable_fields": {
                                "goal": [
                                    "title",
                                    "description",
                                    "category",
                                    "target_date",
                                ],
                                "habit": [
                                    "goal_id",
                                    "name",
                                    "description",
                                    "duration_minutes",
                                    "recurrence_rule",
                                    "start_date",
                                ],
                                "routine_item": [
                                    "goal_id",
                                    "title",
                                    "description",
                                    "item_type",
                                    "schedule_type",
                                    "start_at",
                                    "end_at",
                                    "duration_minutes",
                                    "recurrence_rule",
                                ],
                                "profile": ["name", "style", "description"],
                            },
                        },
                        "execution_diagnosis": state.get(
                            "execution_diagnosis",
                            {},
                        ),
                        "identified_patterns": state.get(
                            "identified_patterns",
                            [],
                        ),
                        "behavioral_state": state.get("behavioral_state", {}),
                        "active_goals": active_goals(list(state.get("goals", [])))[:20],
                        "goals": state.get("goals", [])[:20],
                        "habits": state.get("habits", [])[:30],
                        "routines": state.get("routines", [])[:30],
                        "UNTRUSTED_CONTEXT": {
                            "previous_feedbacks": state.get(
                                "previous_feedbacks",
                                [],
                            )[:5],
                            "recent_messages": state.get(
                                "recent_messages",
                                [],
                            )[-8:],
                            "conversation_summary_en": state.get(
                                "conversation_summary",
                                "",
                            ),
                            "feedbacker_decision_memories": state.get(
                                "feedbacker_decision_memories",
                                [],
                            )[:4],
                        },
                    }
                ),
            )
            model_output = result.parsed.model_dump(mode="json")
            return traced_update(
                state,
                "gerar_hipoteses",
                root_cause_hypotheses=model_output["hypotheses"],
                analysis_model_output=model_output,
                summary_update=result.parsed.updated_summary_en,
                token_usage=model_usage_update(
                    state,
                    result,
                    ModelRole.FEEDBACKER,
                ),
            )
        except AIApplicationError as error:
            return traced_update(
                state,
                "gerar_hipoteses",
                root_cause_hypotheses=[],
                analysis_model_output={
                    "hypotheses": [],
                    "recommendations": [],
                    "success_metrics": [],
                    "response_message": _analysis_fallback(
                        state.get("response_language", "en")
                    ),
                },
                **model_failure_update(
                    state,
                    error,
                    component="feedbacker_model",
                    fallback="deterministic_analysis_only",
                ),
            )

    return traced_update(
        state,
        "gerar_hipoteses",
        root_cause_hypotheses=list(state.get("root_cause_hypotheses", [])),
    )


async def generate_recommendations_node(state: AgentState) -> dict[str, Any]:
    model_recommendations = state.get("analysis_model_output", {}).get(
        "recommendations",
        [],
    )
    return traced_update(
        state,
        "gerar_recomendacoes",
        recommendations=list(state.get("recommendations", model_recommendations)),
    )


async def generate_patch_node(state: AgentState) -> dict[str, Any]:
    generated = state.get("analysis_model_output", {}).get("proposed_patch")
    fallback = (
        _conservative_duration_patch(state)
        if is_explicit_patch_request(state["original_input"])
        else None
    )
    if is_open_ended_patch_request(state["original_input"]):
        generated = fallback or generated
    elif generated is None:
        generated = fallback
    return traced_update(
        state,
        "gerar_patch",
        proposed_patch=state.get("proposed_patch", generated),
        patch_requires_confirmation=(
            state.get("proposed_patch", generated) is not None
        ),
    )


def _conservative_duration_patch(state: AgentState) -> dict[str, Any] | None:
    """Guarantee a safe proposal when Feedbacker omitted an explicit request."""

    metric_by_entity = {
        (str(metric.get("entity_type")), str(metric.get("entity_id"))): metric
        for metric in state.get("habit_metrics", {}).get("entities", [])
    }
    candidates: list[tuple[float, str, dict[str, Any]]] = []
    for entity_type, entities, name_key, metric_type in (
        ("habit", state.get("habits", []), "name", "habit"),
        ("routine_item", state.get("routines", []), "title", "routine"),
    ):
        for entity in entities:
            if entity.get("status") != "active" or not entity.get("id"):
                continue
            duration = int(entity.get("duration_minutes") or 0)
            if duration <= 5:
                continue
            metric = metric_by_entity.get((metric_type, str(entity["id"])), {})
            completion_rate = metric.get("completion_rate")
            missed_weight = 1.0 - float(completion_rate or 0.0)
            expected_weight = min(2.0, int(metric.get("expected_count") or 0) / 10)
            score = duration * (1 + missed_weight + expected_weight)
            candidates.append((score, entity_type, {**entity, "_name_key": name_key}))

    if not candidates:
        return None
    _, entity_type, target = max(
        candidates,
        key=lambda candidate: (candidate[0], str(candidate[2].get("id"))),
    )
    current_duration = int(target["duration_minutes"])
    proposed_duration = max(5, int(round((current_duration * 0.7) / 5) * 5))
    if proposed_duration >= current_duration:
        proposed_duration = max(5, current_duration - 5)
    name = str(target.get(str(target["_name_key"]), "item"))
    language = state.get("response_language", "en")
    reasons = {
        "pt-BR": (
            f"Para começar com uma carga mais compatível com seu tempo, Alfred "
            f"propõe reduzir temporariamente a duração de {name}, de "
            f"{current_duration} para {proposed_duration} minutos."
        ),
        "es": (
            f"Para comenzar con una carga más compatible con tu tiempo, Alfred "
            f"propone reducir temporalmente la duración de {name}, de "
            f"{current_duration} a {proposed_duration} minutos."
        ),
        "fr": (
            f"Pour commencer avec une charge plus compatible avec votre temps, "
            f"Alfred propose de réduire temporairement la durée de {name}, de "
            f"{current_duration} à {proposed_duration} minutes."
        ),
        "en": (
            f"To start with a load that better fits your time, Alfred proposes "
            f"temporarily reducing {name} from {current_duration} to "
            f"{proposed_duration} minutes."
        ),
    }
    metric_names = {
        "pt-BR": "Taxa de conclusão do item",
        "es": "Tasa de finalización del elemento",
        "fr": "Taux de réalisation de l’élément",
        "en": "Item completion rate",
    }
    return {
        "entity_type": entity_type,
        "entity_id": target["id"],
        "operations": [
            {
                "op": "replace",
                "path": "/duration_minutes",
                "value": proposed_duration,
            }
        ],
        "reason": reasons.get(language, reasons["en"]),
        "success_metrics": [
            {
                "name": metric_names.get(language, metric_names["en"]),
                "baseline": "current",
                "target": "increase",
                "evaluation_window_days": 14,
            }
        ],
    }


def _deterministic_patch_response(*, language: str, reason: str) -> str:
    templates = {
        "pt-BR": (
            "Preparei uma alteração segura para você avaliar. {reason} "
            "Nada será alterado sem a sua confirmação."
        ),
        "es": (
            "Preparé un cambio seguro para que lo evalúes. {reason} "
            "Nada se modificará sin tu confirmación."
        ),
        "fr": (
            "J’ai préparé une modification sûre à évaluer. {reason} "
            "Rien ne sera modifié sans votre confirmation."
        ),
        "en": (
            "I prepared a safe change for you to review. {reason} "
            "Nothing will change without your confirmation."
        ),
    }
    return templates.get(language, templates["en"]).format(reason=reason)


async def define_success_metrics_node(state: AgentState) -> dict[str, Any]:
    model_metrics = state.get("analysis_model_output", {}).get(
        "success_metrics",
        [],
    )
    return traced_update(
        state,
        "definir_metricas_sucesso",
        success_metrics=list(state.get("success_metrics", model_metrics)),
    )


async def build_feedbacker_report_node(state: AgentState) -> dict[str, Any]:
    diagnosis = state.get("execution_diagnosis", {})
    model_output = state.get("analysis_model_output", {})
    response_message = str(
        model_output.get(
            "response_message",
            diagnosis.get("summary", "Analysis unavailable."),
        )
    )
    return traced_update(
        state,
        "montar_relatorio_feedbacker",
        analysis_report=state.get(
            "analysis_report",
            {
                "diagnosis": diagnosis,
                "patterns": state.get("identified_patterns", []),
                "hypotheses": state.get("root_cause_hypotheses", []),
                "recommendations": state.get("recommendations", []),
                "success_metrics": state.get("success_metrics", []),
                "metadata": {
                    "capability": "internal_feedbacker",
                    "model_call_count": (
                        state.get("token_usage", {})
                        .get("by_role", {})
                        .get("feedbacker", {})
                        .get("calls", 0)
                    ),
                    "patch_generation_enabled": True,
                },
            },
        ),
        rendered_response=state.get(
            "rendered_response",
            response_message,
        ),
    )


def _analysis_fallback(language: str) -> str:
    return {
        "pt-BR": (
            "Consegui calcular suas métricas, mas não concluir a análise profunda "
            "agora. Nenhuma alteração foi proposta ou aplicada."
        ),
        "es": (
            "Pude calcular tus métricas, pero no completar el análisis profundo "
            "ahora. No se propuso ni aplicó ningún cambio."
        ),
        "fr": (
            "J’ai pu calculer vos métriques, mais pas terminer l’analyse approfondie. "
            "Aucune modification n’a été proposée ou appliquée."
        ),
        "en": (
            "I calculated your metrics but could not complete the deep analysis "
            "right now. No change was proposed or applied."
        ),
    }.get(language, "The deep analysis is temporarily unavailable.")
