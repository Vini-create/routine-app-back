"""Bounded serialization of untrusted model inputs."""

import json
from typing import Any

MAX_MODEL_PAYLOAD_CHARS = 24_000


def bounded_json(
    value: dict[str, Any], *, max_chars: int = MAX_MODEL_PAYLOAD_CHARS
) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )
    if len(encoded) <= max_chars:
        return encoded
    return json.dumps(
        {
            "truncated": True,
            "original_characters": len(encoded),
            "data": encoded[:max_chars],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
