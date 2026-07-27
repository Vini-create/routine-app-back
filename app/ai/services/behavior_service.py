"""Transparent behavioral analytics computed without an LLM."""

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from statistics import median
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dateutil.rrule import rrulestr  # type: ignore[import-untyped]

COMPLETED = "completed"
VACATION = "vacation"


def _safe_timezone(name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(name or "UTC")
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _recurring_dates(
    rule: str,
    *,
    start_at: datetime,
    range_start: date,
    range_end: date,
    user_timezone: ZoneInfo,
    hard_end: date | None = None,
) -> list[date]:
    if range_end < range_start:
        return []
    effective_end = min(range_end, hard_end) if hard_end else range_end
    if effective_end < range_start:
        return []

    lower = datetime.combine(range_start, time.min, tzinfo=user_timezone)
    upper = datetime.combine(effective_end, time.max, tzinfo=user_timezone)
    try:
        occurrences = rrulestr(rule, dtstart=start_at).between(lower, upper, inc=True)
    except (TypeError, ValueError):
        return []
    return sorted({item.astimezone(user_timezone).date() for item in occurrences})


def _entity_occurrences(
    context: dict[str, Any],
    *,
    range_start: date,
    range_end: date,
    user_timezone: ZoneInfo,
) -> tuple[list[dict[str, Any]], int]:
    goals_by_id = {goal["id"]: goal for goal in context.get("goals", [])}
    occurrences: list[dict[str, Any]] = []
    invalid_rules = 0

    habit_logs = {
        (log["habit_id"], _date(log.get("log_date"))): log["status"]
        for log in context.get("habit_logs", [])
    }
    routine_logs = {
        (log["routine_item_id"], _date(log.get("log_date"))): log["status"]
        for log in context.get("routine_logs", [])
    }

    for habit in context.get("habits", []):
        if habit.get("status") != "active":
            continue
        start_date = _date(habit.get("start_date"))
        rule = habit.get("recurrence_rule")
        if start_date is None or not rule:
            invalid_rules += 1
            continue
        goal = goals_by_id.get(habit.get("goal_id"), {})
        target_date = _date(goal.get("target_date"))
        dates = _recurring_dates(
            rule,
            start_at=datetime.combine(start_date, time.min, tzinfo=user_timezone),
            range_start=max(range_start, start_date),
            range_end=range_end,
            user_timezone=user_timezone,
            hard_end=target_date,
        )
        if not dates and range_start <= (target_date or range_end):
            try:
                rrulestr(rule)
            except (TypeError, ValueError):
                invalid_rules += 1
        for occurrence_date in dates:
            status = habit_logs.get((habit["id"], occurrence_date), "uncompleted")
            occurrences.append(
                {
                    "entity_type": "habit",
                    "entity_id": habit["id"],
                    "name": habit["name"],
                    "date": occurrence_date,
                    "status": status,
                    "duration_minutes": max(0, int(habit["duration_minutes"])),
                }
            )

    for item in context.get("routines", []):
        if item.get("status") != "active":
            continue
        start_at = _datetime(item.get("start_at"))
        if start_at is None:
            continue
        local_start = start_at.astimezone(user_timezone)
        end_at = _datetime(item.get("end_at"))
        hard_end = end_at.astimezone(user_timezone).date() if end_at else None
        rule = item.get("recurrence_rule")

        if item.get("schedule_type") == "recurring" and rule:
            dates = _recurring_dates(
                rule,
                start_at=start_at,
                range_start=max(range_start, local_start.date()),
                range_end=range_end,
                user_timezone=user_timezone,
                hard_end=hard_end,
            )
            if not dates:
                try:
                    rrulestr(rule)
                except (TypeError, ValueError):
                    invalid_rules += 1
        else:
            dates = (
                [local_start.date()]
                if range_start <= local_start.date() <= range_end
                else []
            )

        for occurrence_date in dates:
            status = routine_logs.get((item["id"], occurrence_date), "uncompleted")
            occurrences.append(
                {
                    "entity_type": "routine",
                    "entity_id": item["id"],
                    "name": item["title"],
                    "date": occurrence_date,
                    "status": status,
                    "duration_minutes": max(0, int(item["duration_minutes"])),
                }
            )
    return occurrences, invalid_rules


def _completion_rate(completed: int, expected: int) -> float | None:
    return round(completed / expected, 4) if expected else None


def _streaks(occurrences: list[dict[str, Any]]) -> tuple[int, int]:
    counted = [item for item in occurrences if item["status"] != VACATION]
    current = 0
    for item in reversed(counted):
        if item["status"] != COMPLETED:
            break
        current += 1

    longest = 0
    candidate = 0
    for item in counted:
        if item["status"] == COMPLETED:
            candidate += 1
            longest = max(longest, candidate)
        else:
            candidate = 0
    return current, longest


def calculate_behavior_metrics(
    context: dict[str, Any],
    *,
    now: datetime,
    window_days: int = 28,
) -> dict[str, Any]:
    """Create one auditable occurrence series and aggregate it deterministically."""

    user_timezone = _safe_timezone(context.get("profile", {}).get("timezone"))
    local_today = now.astimezone(user_timezone).date()
    range_end = local_today - timedelta(days=1)
    range_start = range_end - timedelta(days=window_days - 1)
    occurrences, invalid_rules = _entity_occurrences(
        context,
        range_start=range_start,
        range_end=range_end,
        user_timezone=user_timezone,
    )
    counted = [item for item in occurrences if item["status"] != VACATION]
    completed = [item for item in counted if item["status"] == COMPLETED]

    per_entity: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in occurrences:
        grouped[(item["entity_type"], item["entity_id"])].append(item)
    for (entity_type, entity_id), items in sorted(grouped.items()):
        entity_counted = [item for item in items if item["status"] != VACATION]
        entity_completed = [
            item for item in entity_counted if item["status"] == COMPLETED
        ]
        current_streak, longest_streak = _streaks(items)
        per_entity.append(
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "name": items[0]["name"],
                "expected_count": len(entity_counted),
                "completed_count": len(entity_completed),
                "completion_rate": _completion_rate(
                    len(entity_completed), len(entity_counted)
                ),
                "current_streak": current_streak,
                "longest_streak": longest_streak,
            }
        )

    by_day: list[dict[str, Any]] = []
    for offset in range(window_days):
        current_date = range_start + timedelta(days=offset)
        day_items = [item for item in counted if item["date"] == current_date]
        day_completed = [item for item in day_items if item["status"] == COMPLETED]
        by_day.append(
            {
                "date": current_date.isoformat(),
                "expected_count": len(day_items),
                "completed_count": len(day_completed),
                "completion_rate": _completion_rate(len(day_completed), len(day_items)),
                "planned_minutes": sum(item["duration_minutes"] for item in day_items),
                "completed_minutes": sum(
                    item["duration_minutes"] for item in day_completed
                ),
            }
        )

    expected_minutes = sum(item["duration_minutes"] for item in counted)
    completed_minutes = sum(item["duration_minutes"] for item in completed)
    return {
        "window": {
            "start_date": range_start.isoformat(),
            "end_date": range_end.isoformat(),
            "days": window_days,
            "excludes_current_day": True,
        },
        "summary": {
            "expected_count": len(counted),
            "completed_count": len(completed),
            "missed_count": len(counted) - len(completed),
            "completion_rate": _completion_rate(len(completed), len(counted)),
            "planned_minutes": expected_minutes,
            "completed_minutes": completed_minutes,
            "completion_minutes_rate": _completion_rate(
                completed_minutes, expected_minutes
            ),
            "vacation_count": len(occurrences) - len(counted),
        },
        "entities": per_entity,
        "daily": by_day,
        "data_quality": {
            "expected_occurrences": len(counted),
            "invalid_recurrence_rules": invalid_rules,
            "sufficient_for_trends": len(counted) >= 6,
        },
    }


def _window_totals(days: list[dict[str, Any]]) -> tuple[int, int, int]:
    return (
        sum(int(day["expected_count"]) for day in days),
        sum(int(day["completed_count"]) for day in days),
        sum(int(day["planned_minutes"]) for day in days),
    )


def detect_behavior_trends(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    daily = metrics.get("daily", [])
    if len(daily) < 28:
        return [{"type": "insufficient_history", "confidence": 0.0}]
    previous = daily[-28:-14]
    recent = daily[-14:]
    previous_expected, previous_completed, previous_minutes = _window_totals(previous)
    recent_expected, recent_completed, recent_minutes = _window_totals(recent)
    if min(previous_expected, recent_expected) < 3:
        return [{"type": "insufficient_history", "confidence": 0.2}]

    previous_rate = previous_completed / previous_expected
    recent_rate = recent_completed / recent_expected
    delta = recent_rate - previous_rate
    direction = (
        "improving" if delta >= 0.15 else "declining" if delta <= -0.15 else "stable"
    )
    confidence = min(1.0, (previous_expected + recent_expected) / 24)
    return [
        {
            "type": "completion_rate",
            "direction": direction,
            "previous_rate": round(previous_rate, 4),
            "recent_rate": round(recent_rate, 4),
            "delta": round(delta, 4),
            "confidence": round(confidence, 4),
        },
        {
            "type": "planned_load",
            "direction": (
                "increasing"
                if recent_minutes > previous_minutes * 1.25
                else "decreasing"
                if previous_minutes > recent_minutes * 1.25
                else "stable"
            ),
            "previous_minutes": previous_minutes,
            "recent_minutes": recent_minutes,
            "confidence": round(confidence, 4),
        },
    ]


def detect_behavior_anomalies(
    metrics: dict[str, Any],
    trends: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    daily = metrics.get("daily", [])
    if len(daily) < 14:
        return []
    previous = daily[-14:-7]
    recent = daily[-7:]
    prev_expected, prev_completed, prev_minutes = _window_totals(previous)
    recent_expected, recent_completed, recent_minutes = _window_totals(recent)
    anomalies: list[dict[str, Any]] = []

    if prev_expected >= 3 and recent_expected >= 3:
        previous_rate = prev_completed / prev_expected
        recent_rate = recent_completed / recent_expected
        if previous_rate - recent_rate >= 0.30:
            anomalies.append(
                {
                    "type": "completion_drop",
                    "severity": "moderate",
                    "evidence": {
                        "previous_7d_rate": round(previous_rate, 4),
                        "recent_7d_rate": round(recent_rate, 4),
                    },
                }
            )
    if recent_expected >= 3 and recent_completed == 0:
        anomalies.append(
            {
                "type": "recent_inactivity",
                "severity": "high",
                "evidence": {"expected_7d": recent_expected},
            }
        )
    if recent_minutes >= max(120, round(prev_minutes * 1.5)):
        anomalies.append(
            {
                "type": "planned_load_spike",
                "severity": "moderate",
                "evidence": {
                    "previous_7d_minutes": prev_minutes,
                    "recent_7d_minutes": recent_minutes,
                },
            }
        )

    planned_values = [
        int(day["planned_minutes"]) for day in daily if day["planned_minutes"]
    ]
    if planned_values:
        baseline = median(planned_values)
        last_day = int(daily[-1]["planned_minutes"])
        if baseline and last_day >= max(180, baseline * 3):
            anomalies.append(
                {
                    "type": "single_day_overload",
                    "severity": "moderate",
                    "evidence": {
                        "baseline_daily_minutes": baseline,
                        "last_day_minutes": last_day,
                    },
                }
            )
    return anomalies


def predict_dropout_risk(
    metrics: dict[str, Any],
    trends: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return an explainable heuristic score, never a clinical prediction."""

    expected = int(metrics.get("summary", {}).get("expected_count", 0))
    completion_rate = metrics.get("summary", {}).get("completion_rate")
    score = 0.0
    reasons: list[str] = []

    if completion_rate is not None:
        if completion_rate < 0.25:
            score += 0.35
            reasons.append("very_low_completion")
        elif completion_rate < 0.50:
            score += 0.20
            reasons.append("low_completion")

    completion_trend = next(
        (trend for trend in trends if trend.get("type") == "completion_rate"),
        None,
    )
    if completion_trend and completion_trend.get("direction") == "declining":
        score += 0.20
        reasons.append("declining_completion")
    anomaly_types = {anomaly["type"] for anomaly in anomalies}
    if "recent_inactivity" in anomaly_types:
        score += 0.30
        reasons.append("recent_inactivity")
    if {"planned_load_spike", "single_day_overload"} & anomaly_types:
        score += 0.15
        reasons.append("possible_overload")

    score = round(min(score, 1.0), 4)
    level = "high" if score >= 0.60 else "moderate" if score >= 0.30 else "low"
    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "confidence": round(min(1.0, expected / 20), 4),
        "method": "transparent_rules_v1",
        "is_clinical_prediction": False,
        "limitations": (
            "Behavioral heuristic based only on recorded routine activity; "
            "missing logs may not mean abandonment."
        ),
    }
