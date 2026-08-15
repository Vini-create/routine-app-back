"""Bounded local retrieval for original Alfred motivational phrases."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

PHRASES_PATH = (
    Path(__file__).resolve().parents[3]
    / "Alfred"
    / "rag"
    / "corpus"
    / "editorial"
    / "motivational_phrases.json"
)
SUPPORTED_LANGUAGES = frozenset({"pt-BR", "en", "es", "fr"})
MOTIVATIONAL_REQUEST = re.compile(
    r"\b(?:motiv|desanim|sem vontade|incentiv|inspir|quero desistir|"
    r"give me a boost|encourage|animo|courage|motivation)\w*\b"
)
TOPIC_TERMS = {
    "motivation": ("motiv", "desanim", "sem vontade", "incentiv", "inspir"),
    "resilience": ("desist", "recomec", "fracass", "falhei", "difícil", "dificil"),
    "habits": ("habito", "habit", "constancia", "consistency", "rotina"),
    "consistency": ("constancia", "consistency", "frequencia", "retomar"),
    "goals": ("meta", "goal", "objetivo", "objectif"),
    "planning": ("plano", "planej", "plan", "agenda"),
    "study-and-learning": ("estud", "study", "aprender", "learning"),
    "procrastination": ("procrast", "adiando", "enrolando", "posterg"),
    "self-regulation": ("disciplina", "autocontrole", "self control"),
}


def _canonical(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )


def _was_recently_used(phrase: str, recent_messages: str) -> bool:
    phrase_words = set(re.findall(r"\b\w{4,}\b", _canonical(phrase)))
    recent_words = set(re.findall(r"\b\w{4,}\b", _canonical(recent_messages)))
    if not phrase_words:
        return False
    return len(phrase_words & recent_words) / len(phrase_words) >= 0.7


@lru_cache(maxsize=1)
def load_editorial_phrases() -> tuple[dict[str, Any], ...]:
    records = json.loads(PHRASES_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError("The Alfred editorial phrase collection is empty.")
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for record in records:
        phrase_id = record.get("phrase_id")
        topics = record.get("topics")
        texts = record.get("texts")
        if not isinstance(phrase_id, str) or phrase_id in seen:
            raise ValueError("An Alfred editorial phrase has an invalid ID.")
        if not isinstance(topics, list) or not topics:
            raise ValueError(f"Editorial phrase '{phrase_id}' has no topics.")
        if not isinstance(texts, dict) or set(texts) != SUPPORTED_LANGUAGES:
            raise ValueError(f"Editorial phrase '{phrase_id}' is not localized.")
        if any(
            not isinstance(text, str) or not text.strip() for text in texts.values()
        ):
            raise ValueError(f"Editorial phrase '{phrase_id}' has empty text.")
        seen.add(phrase_id)
        validated.append(record)
    return tuple(validated)


def retrieve_motivational_phrase(
    message: str,
    *,
    response_language: str,
    recent_assistant_messages: list[str],
) -> dict[str, str] | None:
    """Return at most one relevant, non-repeated phrase for explicit motivation."""

    canonical = _canonical(message)
    if not MOTIVATIONAL_REQUEST.search(canonical):
        return None
    topics = {
        topic
        for topic, terms in TOPIC_TERMS.items()
        if any(term in canonical for term in terms)
    } or {"motivation"}
    recent = " ".join(recent_assistant_messages[-8:])
    candidates = [
        phrase
        for phrase in load_editorial_phrases()
        if topics.intersection(phrase["topics"])
        and not _was_recently_used(phrase["texts"][response_language], recent)
    ]
    if not candidates:
        return None
    digest = hashlib.sha256(canonical.encode("utf-8")).digest()
    selected = candidates[int.from_bytes(digest[:4], "big") % len(candidates)]
    return {
        "phrase_id": selected["phrase_id"],
        "text": selected["texts"][response_language],
        "origin": "alfred_editorial",
    }
