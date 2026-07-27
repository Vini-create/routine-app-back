"""Dependencies that exist only while one graph invocation is running."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.errors import AIApplicationError, AIErrorCode

if TYPE_CHECKING:
    from app.ai.models.gateway import AIModelGateway
    from app.ai.retrieval.hybrid import KnowledgeRetriever


@dataclass(frozen=True, slots=True)
class GraphRuntimeContext:
    """Non-serializable dependencies kept outside ``AgentState``.

    LangGraph passes this object directly to nodes that declare a ``runtime``
    parameter. Database sessions and the authenticated identity must never be
    copied into graph state because state may later be checkpointed or traced.
    """

    session: AsyncSession | None = None
    authenticated_user_id: UUID | None = None
    now: datetime | None = None
    history_days: int = 28
    model_gateway: "AIModelGateway | None" = None
    knowledge_retriever: "KnowledgeRetriever | None" = None

    def current_time(self) -> datetime:
        current = self.now or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "GraphRuntimeContext.now must be timezone-aware.",
            )
        return current

    def require_user_id(self, state_user_id: str) -> UUID:
        """Validate that graph state cannot select another user's records."""

        try:
            parsed_state_user_id = UUID(state_user_id)
        except ValueError as exc:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "AgentState.user_id must be a valid UUID.",
            ) from exc

        if self.authenticated_user_id is None:
            raise AIApplicationError(
                AIErrorCode.USER_CONTEXT_FORBIDDEN,
                "An authenticated user is required to load graph context.",
            )
        if parsed_state_user_id != self.authenticated_user_id:
            raise AIApplicationError(
                AIErrorCode.USER_CONTEXT_FORBIDDEN,
                "The graph state does not belong to the authenticated user.",
            )
        return parsed_state_user_id

    def __post_init__(self) -> None:
        if not 7 <= self.history_days <= 90:
            raise ValueError("history_days must be between 7 and 90")
        if self.now is not None:
            self.current_time()
