"""Localized simple-data answers that never call a model."""

import unicodedata
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langgraph.runtime import Runtime

from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState


def _canonical(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character for character in folded if not unicodedata.combining(character)
    )


def _now(runtime: Runtime[GraphRuntimeContext] | None) -> datetime:
    if runtime is not None and runtime.context is not None:
        return runtime.context.current_time()
    return datetime.now(timezone.utc)


def _local_today(state: AgentState, now: datetime) -> str:
    timezone_name = str(state.get("profile", {}).get("timezone", "UTC"))
    try:
        user_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        user_timezone = ZoneInfo("UTC")
    return now.astimezone(user_timezone).date().isoformat()


def _copy(language: str, key: str, **values: Any) -> str:
    copies = {
        "pt-BR": {
            "habits_today": "Você concluiu {count} hábito(s) hoje.",
            "active_habits": "Você tem {count} hábito(s) ativo(s).",
            "active_goals": "Você tem {count} meta(s) ativa(s).",
            "completion_rate": (
                "Sua taxa de conclusão nos últimos 28 dias completos é {rate}%."
            ),
            "streak": "Sua maior sequência atual é de {count} ocorrência(s).",
            "summary": (
                "Nos últimos 28 dias completos: {completed} de {expected} "
                "ocorrências concluídas ({rate}%)."
            ),
        },
        "en": {
            "habits_today": "You completed {count} habit(s) today.",
            "active_habits": "You have {count} active habit(s).",
            "active_goals": "You have {count} active goal(s).",
            "completion_rate": (
                "Your completion rate over the last 28 completed days is {rate}%."
            ),
            "streak": "Your longest current streak is {count} occurrence(s).",
            "summary": (
                "Over the last 28 completed days: {completed} of {expected} "
                "occurrences completed ({rate}%)."
            ),
        },
        "es": {
            "habits_today": "Completaste {count} hábito(s) hoy.",
            "active_habits": "Tienes {count} hábito(s) activo(s).",
            "active_goals": "Tienes {count} meta(s) activa(s).",
            "completion_rate": (
                "Tu tasa de finalización en los últimos 28 días completos es {rate}%."
            ),
            "streak": "Tu mayor racha actual es de {count} ocurrencia(s).",
            "summary": (
                "En los últimos 28 días completos: {completed} de {expected} "
                "ocurrencias completadas ({rate}%)."
            ),
        },
        "fr": {
            "habits_today": "Vous avez terminé {count} habitude(s) aujourd'hui.",
            "active_habits": "Vous avez {count} habitude(s) active(s).",
            "active_goals": "Vous avez {count} objectif(s) actif(s).",
            "completion_rate": (
                "Votre taux de réalisation sur les 28 derniers jours complets "
                "est de {rate}%."
            ),
            "streak": "Votre plus longue série actuelle est de {count} occurrence(s).",
            "summary": (
                "Sur les 28 derniers jours complets : {completed} occurrences "
                "terminées sur {expected} ({rate}%)."
            ),
        },
    }
    return copies.get(language, copies["en"])[key].format(**values)


async def answer_deterministic_query_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    message = _canonical(state.get("normalized_input", state["original_input"]))
    language = state.get("response_language", "en")
    metrics = state.get("habit_metrics", {})
    summary = metrics.get("summary", {})
    today = _local_today(state, _now(runtime))

    if (
        any(term in message for term in ("hoje", "today", "hoy", "aujourd"))
        and any(term in message for term in ("conclu", "complet", "termin"))
        and any(term in message for term in ("habito", "habit", "habitude"))
    ):
        count = sum(
            log.get("status") == "completed" and log.get("log_date") == today
            for log in state.get("habit_logs", [])
        )
        response = _copy(language, "habits_today", count=count)
    elif any(term in message for term in ("meta", "goal", "objectif")):
        count = sum(
            goal.get("status") in {"active", "in_progress"}
            for goal in state.get("goals", [])
        )
        response = _copy(language, "active_goals", count=count)
    elif any(term in message for term in ("taxa", "rate", "taux", "porcent")):
        rate = round(float(summary.get("completion_rate") or 0) * 100, 1)
        response = _copy(language, "completion_rate", rate=rate)
    elif any(term in message for term in ("sequencia", "streak", "racha", "serie")):
        current_streak = max(
            (
                int(entity.get("current_streak", 0))
                for entity in metrics.get("entities", [])
            ),
            default=0,
        )
        response = _copy(language, "streak", count=current_streak)
    elif any(term in message for term in ("ativo", "active", "actif")):
        count = sum(
            habit.get("status") == "active" for habit in state.get("habits", [])
        )
        response = _copy(language, "active_habits", count=count)
    else:
        expected = int(summary.get("expected_count", 0))
        completed = int(summary.get("completed_count", 0))
        rate = round(float(summary.get("completion_rate") or 0) * 100, 1)
        response = _copy(
            language,
            "summary",
            expected=expected,
            completed=completed,
            rate=rate,
        )

    return traced_update(
        state,
        "responder_dado_simples",
        rendered_response=state.get("rendered_response", response),
    )
