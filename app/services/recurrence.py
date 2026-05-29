from dateutil.rrule import rrulestr
from datetime import datetime

ALLOWED_RRULE_FREQS = {"DAILY", "WEEKLY", "MONTHLY", "YEARLY"}

def validate_allowed_frequency(rule: str) -> None:
    parts = rule.split(";")

    freq_part = next(
        (part for part in parts if part.startswith("FREQ=")),
        None,
    )

    if freq_part is None:
        raise ValueError("recurrence_rule must include FREQ")

    freq = freq_part.removeprefix("FREQ=")

    if freq not in ALLOWED_RRULE_FREQS:
        raise ValueError("recurrence frequency is not allowed")

def validate_recurrence_rule(rule: str) -> None:
    validate_allowed_frequency(rule)
    try:
        rrulestr(rule)
    except Exception:
        raise ValueError("Invalid recurrence_rule")


def get_occurrences(rule: str, start_at: datetime, range_start: datetime, range_end: datetime):
    recurrence = rrulestr(rule, dtstart=start_at)
    return recurrence.between(range_start, range_end, inc=True)