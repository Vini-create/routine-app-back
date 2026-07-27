"""Domain errors returned by the AI application layer."""

from enum import StrEnum


class AIErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    IDEMPOTENCY_KEY_REUSED = "idempotency_key_reused"
    CONVERSATION_NOT_FOUND = "conversation_not_found"
    CONVERSATION_FORBIDDEN = "conversation_forbidden"
    USER_CONTEXT_FORBIDDEN = "user_context_forbidden"
    USER_CONTEXT_UNAVAILABLE = "user_context_unavailable"
    PLAN_UNAVAILABLE = "plan_unavailable"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DAILY_QUOTA_EXCEEDED = "daily_quota_exceeded"
    DAILY_STANDARD_LIMIT_EXCEEDED = "daily_standard_limit_exceeded"
    DAILY_RAG_LIMIT_EXCEEDED = "daily_rag_limit_exceeded"
    WEEKLY_DEEP_ANALYSIS_LIMIT_EXCEEDED = "weekly_deep_analysis_limit_exceeded"
    CONCURRENT_STREAM_LIMIT_EXCEEDED = "concurrent_stream_limit_exceeded"
    GLOBAL_COST_LIMIT_EXCEEDED = "global_cost_limit_exceeded"
    USAGE_RESERVATION_NOT_FOUND = "usage_reservation_not_found"
    USAGE_RESERVATION_ALREADY_CLOSED = "usage_reservation_already_closed"
    PATCH_NOT_FOUND = "patch_not_found"
    PATCH_FORBIDDEN = "patch_forbidden"
    PATCH_EXPIRED = "patch_expired"
    PATCH_ALREADY_RESOLVED = "patch_already_resolved"
    MODEL_UNAVAILABLE = "model_unavailable"
    MODEL_INVALID_OUTPUT = "model_invalid_output"
    GRAPH_EXECUTION_FAILED = "graph_execution_failed"


class AIApplicationError(Exception):
    """Expected error that can be translated into a stable API response."""

    def __init__(
        self,
        code: AIErrorCode,
        message: str,
        *,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.request_id = request_id
