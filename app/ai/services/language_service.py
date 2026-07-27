"""Offline language detection and response-localization helpers."""

from dataclasses import dataclass
from functools import lru_cache
import re

from lingua import Language, LanguageDetector, LanguageDetectorBuilder

SUPPORTED_LANGUAGE_CODES = frozenset({"pt-BR", "en", "es", "fr"})

_LINGUA_TO_CODE = {
    Language.PORTUGUESE: "pt-BR",
    Language.ENGLISH: "en",
    Language.SPANISH: "es",
    Language.FRENCH: "fr",
}
_PROFILE_TO_CODE = {
    "portuguese_br": "pt-BR",
    "pt-br": "pt-BR",
    "pt_br": "pt-BR",
    "english_us": "en",
    "en-us": "en",
    "en_us": "en",
    "spanish": "es",
    "es": "es",
    "french": "fr",
    "fr": "fr",
}
_LANGUAGE_NEUTRAL_INPUTS = frozenset(
    {
        "ok",
        "okay",
        "kk",
        "k",
        "👍",
        "👌",
        "🙂",
        "😀",
        "❤️",
    }
)
_DISAMBIGUATION_MARKERS = {
    "pt-BR": frozenset(
        {
            "agora",
            "com",
            "como",
            "estou",
            "eu",
            "hábitos",
            "me",
            "meu",
            "minha",
            "não",
            "quero",
            "rotina",
            "você",
        }
    ),
    "en": frozenset({"habit", "how", "i", "my", "routine", "the", "today", "want"}),
    "es": frozenset({"ahora", "cómo", "estoy", "mis", "quiero", "rutina", "yo"}),
    "fr": frozenset(
        {"aujourd", "comment", "habitude", "je", "ma", "mes", "routine", "veux"}
    ),
}


@dataclass(frozen=True, slots=True)
class LanguageDetection:
    language: str
    confidence: float
    reliable: bool
    source: str = "lingua_offline"


@lru_cache(maxsize=1)
def _detector() -> LanguageDetector:
    """Build only the four product languages and load models lazily."""

    return LanguageDetectorBuilder.from_languages(
        Language.PORTUGUESE,
        Language.ENGLISH,
        Language.SPANISH,
        Language.FRENCH,
    ).build()


def detect_language(value: str) -> LanguageDetection:
    normalized = " ".join(value.casefold().split())
    if not normalized or normalized in _LANGUAGE_NEUTRAL_INPUTS:
        return LanguageDetection("und", 0.0, False, "ambiguous_short_input")

    words = set(re.findall(r"[^\W\d_]+", normalized, flags=re.UNICODE))
    marker_scores = {
        language: len(words & markers)
        for language, markers in _DISAMBIGUATION_MARKERS.items()
    }
    marker_language, marker_score = max(
        marker_scores.items(),
        key=lambda item: item[1],
    )
    competing_score = max(
        score
        for language, score in marker_scores.items()
        if language != marker_language
    )
    if marker_score >= 2 and marker_score > competing_score:
        confidence = round(marker_score / max(3, len(words)), 4)
        return LanguageDetection(
            marker_language,
            max(0.7, confidence),
            True,
            "product_lexicon_then_lingua",
        )

    confidence_values = _detector().compute_language_confidence_values(value)
    if not confidence_values:
        return LanguageDetection("und", 0.0, False)

    best = confidence_values[0]
    second_value = confidence_values[1].value if len(confidence_values) > 1 else 0.0
    confidence = round(float(best.value), 4)
    relative_distance = confidence - float(second_value)
    reliable = confidence >= 0.55 and relative_distance >= 0.12
    # A low-margin candidate is still preferable for localized safety copy.
    # ``reliable`` remains false so downstream semantic decisions cannot treat
    # it as a high-confidence classification.
    language = (
        _LINGUA_TO_CODE.get(best.language, "und") if confidence >= 0.35 else "und"
    )
    return LanguageDetection(language, confidence, reliable)


def normalize_language_code(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.casefold().replace("_", "-")
    if normalized in {code.casefold() for code in SUPPORTED_LANGUAGE_CODES}:
        return "pt-BR" if normalized == "pt-br" else normalized
    return _PROFILE_TO_CODE.get(value.casefold())


def resolve_response_language(
    detected_language: str | None,
    profile_language: str | None = None,
) -> str:
    """Prefer reliable input language, then the user's saved preference."""

    detected = normalize_language_code(detected_language)
    if detected is not None:
        return detected
    profile = normalize_language_code(profile_language)
    return profile or "en"
