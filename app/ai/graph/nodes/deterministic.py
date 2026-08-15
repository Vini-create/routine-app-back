"""Localized simple-data answers that never call a model."""

import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langgraph.runtime import Runtime

from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.services.behavior_service import scheduled_occurrences


def _canonical(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character for character in folded if not unicodedata.combining(character)
    )


def _now(runtime: Runtime[GraphRuntimeContext] | None) -> datetime:
    if runtime is not None and runtime.context is not None:
        return runtime.context.current_time()
    return datetime.now(timezone.utc)


def _local_date(state: AgentState, now: datetime) -> date:
    timezone_name = str(state.get("profile", {}).get("timezone", "UTC"))
    try:
        user_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        user_timezone = ZoneInfo("UTC")
    return now.astimezone(user_timezone).date()


def _requested_date(message: str, today: date) -> date:
    if any(term in message for term in ("amanha", "tomorrow", "manana", "demain")):
        return today + timedelta(days=1)
    if any(term in message for term in ("ontem", "yesterday", "ayer", "hier")):
        return today - timedelta(days=1)
    iso = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", message)
    if iso:
        try:
            return date.fromisoformat(iso.group(0))
        except ValueError:
            pass
    local = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", message)
    if local:
        try:
            return date(int(local.group(3)), int(local.group(2)), int(local.group(1)))
        except ValueError:
            pass
    return today


def _is_schedule_list_request(message: str) -> bool:
    asks_which = any(
        term in message
        for term in (
            "quais",
            "liste",
            "listar",
            "mostre",
            "o que tenho",
            "which",
            "list",
            "show",
            "cuales",
            "muestra",
        )
    )
    mentions_schedule = any(
        term in message
        for term in (
            "tarefa",
            "atividade",
            "agenda",
            "programacao",
            "rotina",
            "task",
            "activit",
            "schedule",
            "tarea",
        )
    )
    return asks_which and mentions_schedule


def _schedule_response(language: str, target: date, items: list[dict[str, Any]]) -> str:
    labels = {
        "pt-BR": (
            "Sua programação de",
            "Não há tarefas ou hábitos programados para",
            "concluída",
            "pendente",
            "min",
        ),
        "en": (
            "Your schedule for",
            "There are no tasks or habits scheduled for",
            "completed",
            "pending",
            "min",
        ),
        "es": (
            "Tu programación del",
            "No hay tareas ni hábitos programados para",
            "completada",
            "pendiente",
            "min",
        ),
        "fr": (
            "Votre programme du",
            "Aucune tâche ou habitude n’est prévue pour le",
            "terminée",
            "à faire",
            "min",
        ),
    }
    title, empty, completed, pending, minutes = labels.get(language, labels["en"])
    shown_date = target.strftime("%d/%m/%Y")
    if not items:
        return f"{empty} {shown_date}."
    lines = [f"**{title} {shown_date} ({len(items)} itens):**"]
    for index, item in enumerate(items, 1):
        time_label = (
            f" às {item['start_time']}"
            if language == "pt-BR" and item.get("start_time")
            else f" — {item['start_time']}"
            if item.get("start_time")
            else ""
        )
        status = completed if item.get("status") == "completed" else pending
        duration = int(item.get("duration_minutes") or 0)
        lines.append(
            f"{index}. **{item['name']}**{time_label} · {duration} {minutes} · {status}"
        )
    return "\n".join(lines)


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
    local_today = _local_date(state, _now(runtime))
    today = local_today.isoformat()

    if _is_schedule_list_request(message):
        target_date = _requested_date(message, local_today)
        items = scheduled_occurrences(
            {
                "profile": state.get("profile", {}),
                "goals": state.get("goals", []),
                "habits": state.get("habits", []),
                "routines": state.get("routines", []),
                "habit_logs": state.get("habit_logs", []),
                "routine_logs": state.get("routine_logs", []),
            },
            target_date=target_date,
        )
        response = _schedule_response(language, target_date, items)
    elif (
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
