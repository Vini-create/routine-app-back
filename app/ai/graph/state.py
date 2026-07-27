"""Serializable state contract for the unified LangGraph workflow."""

from typing import Any, NotRequired, Required, TypedDict

from app.ai.domain.enums import (
    AlfredCapability,
    InternalRoute,
    PatchDecision,
    SafetyLevel,
    SelectedSkill,
)


class AgentState(TypedDict):
    """State passed between LangGraph nodes.

    Nodes receive the accumulated state and return only the fields they changed.
    Runtime clients, database sessions, secrets, tokens and billing
    configuration must never be stored here.
    """

    # Required graph input
    request_id: Required[str]
    user_id: Required[str]
    conversation_id: Required[str | None]
    selected_skill: Required[SelectedSkill]
    original_input: Required[str]

    # Optional request context
    screen_context: NotRequired[dict[str, Any] | None]
    idempotency_key: NotRequired[str | None]
    idempotency_fingerprint: NotRequired[str]

    # Language and normalization
    detected_language: NotRequired[str]
    response_language: NotRequired[str]
    language_detection_source: NotRequired[str]
    translation_confidence: NotRequired[float]
    normalized_input: NotRequired[str]

    # Safety
    prompt_injection_suspected: NotRequired[bool]
    prompt_injection_score: NotRequired[float]
    prompt_injection_signals: NotRequired[list[str]]
    safety_level: NotRequired[SafetyLevel]
    safety_categories: NotRequired[list[str]]
    safety_risk_score: NotRequired[float]
    security_restrictions: NotRequired[list[str]]
    blocked: NotRequired[bool]
    safe_response: NotRequired[dict[str, Any]]

    # Raw context
    profile: NotRequired[dict[str, Any]]
    goals: NotRequired[list[dict[str, Any]]]
    routines: NotRequired[list[dict[str, Any]]]
    habits: NotRequired[list[dict[str, Any]]]
    habit_logs: NotRequired[list[dict[str, Any]]]
    routine_logs: NotRequired[list[dict[str, Any]]]
    previous_feedbacks: NotRequired[list[dict[str, Any]]]
    recent_messages: NotRequired[list[dict[str, Any]]]
    history_window: NotRequired[dict[str, str]]
    conversation_summary: NotRequired[str]
    relevant_memories: NotRequired[list[dict[str, Any]]]
    feedbacker_decision_memories: NotRequired[list[dict[str, Any]]]
    user_context: NotRequired[dict[str, Any]]

    # Behavioral intelligence
    habit_metrics: NotRequired[dict[str, Any]]
    detected_trends: NotRequired[list[dict[str, Any]]]
    detected_anomalies: NotRequired[list[dict[str, Any]]]
    dropout_risk: NotRequired[dict[str, Any]]
    behavioral_state: NotRequired[dict[str, Any]]

    # Intent and route
    detected_intent: NotRequired[str]
    intent_confidence: NotRequired[float]
    route: NotRequired[InternalRoute]
    capability: NotRequired[AlfredCapability | None]
    route_confidence: NotRequired[float]
    route_reason: NotRequired[str]
    required_context: NotRequired[list[str]]

    # RAG
    needs_rag: NotRequired[bool]
    rag_destination: NotRequired[str]
    retrieval_topics: NotRequired[list[str]]
    retrieval_query: NotRequired[str]
    retrieved_documents: NotRequired[list[dict[str, Any]]]
    retrieval_confidence: NotRequired[float]
    retrieval_coverage: NotRequired[float]
    insufficient_evidence: NotRequired[bool]
    evidence_pack: NotRequired[dict[str, Any]]

    # Conversational capability
    alfred_strategy: NotRequired[str]
    alfred_plan: NotRequired[dict[str, Any]]
    alfred_intervention: NotRequired[dict[str, Any]]
    rendered_response: NotRequired[str]

    # Internal analytical capability
    execution_diagnosis: NotRequired[dict[str, Any]]
    identified_patterns: NotRequired[list[dict[str, Any]]]
    root_cause_hypotheses: NotRequired[list[dict[str, Any]]]
    recommendations: NotRequired[list[dict[str, Any]]]
    analysis_model_output: NotRequired[dict[str, Any]]
    analysis_report: NotRequired[dict[str, Any]]

    # Patch and intervention evaluation
    proposed_patch: NotRequired[dict[str, Any] | None]
    success_metrics: NotRequired[list[dict[str, Any]]]
    patch_validation: NotRequired[dict[str, Any]]
    patch_simulation: NotRequired[dict[str, Any]]
    patch_requires_confirmation: NotRequired[bool]
    patch_id: NotRequired[str | None]
    human_decision: NotRequired[PatchDecision | None]

    # Critic
    critic_required: NotRequired[bool]
    critic_output: NotRequired[dict[str, Any]]
    revision_count: NotRequired[int]
    schema_valid: NotRequired[bool]
    validation_errors: NotRequired[list[str]]

    # Memory
    memory_candidates: NotRequired[list[dict[str, Any]]]
    memories_to_store: NotRequired[list[dict[str, Any]]]
    summary_update: NotRequired[str | None]

    # Response
    final_response: NotRequired[dict[str, Any]]

    # Resilience and observability
    degraded_mode: NotRequired[bool]
    unavailable_components: NotRequired[list[str]]
    fallback_used: NotRequired[str | None]
    errors: NotRequired[list[dict[str, Any]]]
    trace_data: NotRequired[dict[str, Any]]
    token_usage: NotRequired[dict[str, Any]]
    latency_metrics: NotRequired[dict[str, float]]
