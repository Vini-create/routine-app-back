"""Stable enums used by the unified Alfred contract."""

from enum import StrEnum


class SelectedSkill(StrEnum):
    """Optional frontend hint.

    A selected skill improves routing context, but never forces an internal
    route. In particular, ``feedbacker`` is intentionally not a valid public
    skill.
    """

    AUTO = "auto"
    CONVERSAR = "conversar"
    ANALISAR_PROGRESSO = "analisar_progresso"
    REORGANIZAR_ROTINA = "reorganizar_rotina"
    CRIAR_PLANO = "criar_plano"
    CONSULTAR_CONHECIMENTO = "consultar_conhecimento"


class AlfredCapability(StrEnum):
    """The four implementation capabilities available behind Alfred.

    This enum is architectural vocabulary, not a public route selector.
    """

    DETERMINISTIC = "deterministic"
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    KNOWLEDGE_AUGMENTED = "knowledge_augmented"


class InternalRoute(StrEnum):
    """Concrete route chosen by the graph after safety and intent analysis."""

    SAFE_RESPONSE = "safe_response"
    DETERMINISTIC = "deterministic"
    ALFRED = "alfred"
    FEEDBACKER = "feedbacker"
    RAG_THEN_ALFRED = "rag_then_alfred"
    RAG_THEN_FEEDBACKER = "rag_then_feedbacker"


def capability_for_route(
    route: InternalRoute,
) -> AlfredCapability | None:
    """Map an executable route to one of Alfred's four product capabilities."""

    return {
        InternalRoute.DETERMINISTIC: AlfredCapability.DETERMINISTIC,
        InternalRoute.ALFRED: AlfredCapability.CONVERSATIONAL,
        InternalRoute.FEEDBACKER: AlfredCapability.ANALYTICAL,
        InternalRoute.RAG_THEN_ALFRED: AlfredCapability.KNOWLEDGE_AUGMENTED,
        InternalRoute.RAG_THEN_FEEDBACKER: AlfredCapability.KNOWLEDGE_AUGMENTED,
        InternalRoute.SAFE_RESPONSE: None,
    }[route]


class SafetyLevel(StrEnum):
    """Severity assigned by the safety pipeline."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class PatchDecision(StrEnum):
    """Decision supplied by the user while resuming a pending patch."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EDITED = "edited"


class MemoryType(StrEnum):
    """Supported retention strategies for an Alfred memory."""

    SHORT_TERM = "short_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
