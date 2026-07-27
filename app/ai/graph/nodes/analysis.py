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
                        "execution_diagnosis": state.get(
                            "execution_diagnosis",
                            {},
                        ),
                        "identified_patterns": state.get(
                            "identified_patterns",
                            [],
                        ),
                        "behavioral_state": state.get("behavioral_state", {}),
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
    return traced_update(
        state,
        "gerar_patch",
        proposed_patch=state.get("proposed_patch", generated),
        patch_requires_confirmation=(
            state.get("proposed_patch", generated) is not None
        ),
    )


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
