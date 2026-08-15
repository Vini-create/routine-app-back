"""Production orchestration for the single public Alfred entry point."""

import asyncio
import hashlib
import json
import logging
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from time import perf_counter
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.enums import InternalRoute
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.graph import GRAPH_RECURSION_LIMIT, GraphRuntimeContext, build_graph
from app.ai.graph.nodes._model import model_usage_update
from app.ai.graph.nodes.entry import (
    assess_personal_safety,
    assess_prompt_injection,
)
from app.ai.graph.state import AgentState
from app.ai.models.gateway import (
    AIModelGateway,
    ModelRole,
    build_default_model_gateway,
)
from app.ai.prompts.payloads import bounded_json
from app.ai.prompts.routing import build_routing_system_prompt
from app.ai.repositories.persistence_repository import (
    find_checkpoint_replay,
    normalize_conversation_summary,
    resolve_conversation,
    save_message,
)
from app.ai.retrieval.runtime import build_default_knowledge_retriever
from app.ai.schemas.requests import AIInvokeRequest
from app.ai.schemas.responses import AIInvokeResponse, AIUsage
from app.ai.schemas.routing import RoutingDecision
from app.ai.services.routing_service import (
    classify_route,
    needs_routine_goal_clarification,
)
from app.ai.services.usage_service import (
    confirm_ai_usage,
    fail_ai_usage,
    get_usage_snapshot,
    release_ai_usage,
    reserve_ai_usage,
)
from app.billing.service import require_active_billing_access
from app.core.config import settings
from app.models.ai import AIGraphCheckpoint
from app.models.auth import User

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def default_model_gateway() -> AIModelGateway:
    return build_default_model_gateway()


@lru_cache(maxsize=1)
def default_graph() -> Any:
    """Compile the immutable LangGraph topology once per worker."""

    return build_graph()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "value"):
        return _json_safe(value.value)
    if isinstance(value, (UUID, date, datetime)):
        return str(value)
    return value


def _token_usage_seed() -> dict[str, Any]:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "model_calls": 0,
        "by_role": {},
    }


def _request_fingerprint(payload: AIInvokeRequest) -> str:
    """Bind one idempotency key to one canonical public request payload."""

    serialized = json.dumps(
        payload.model_dump(mode="json", exclude={"idempotency_key"}),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _validate_replay_payload(
    checkpoint: AIGraphCheckpoint,
    payload: AIInvokeRequest,
) -> None:
    stored = checkpoint.state or {}
    expected_fingerprint = stored.get("idempotency_fingerprint")
    matches = (
        expected_fingerprint == _request_fingerprint(payload)
        if expected_fingerprint is not None
        else (
            stored.get("original_input") == payload.message
            and str(stored.get("selected_skill", "auto"))
            == payload.selected_skill.value
            and stored.get("screen_context") == payload.screen_context
            and (
                payload.conversation_id is None
                or stored.get("conversation_id") == str(payload.conversation_id)
            )
        )
    )
    if not matches:
        raise AIApplicationError(
            AIErrorCode.IDEMPOTENCY_KEY_REUSED,
            (
                "This idempotency key was already used for a different Alfred "
                "request. Generate a new key for each new message."
            ),
        )


class AIOrchestrator:
    """Owns identity, billing, graph execution and durable request boundaries."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        user: User,
        model_gateway: AIModelGateway | None = None,
    ) -> None:
        self._session = session
        self._user = user
        self._model_gateway = model_gateway or default_model_gateway()

    async def _resolve_route(
        self,
        payload: AIInvokeRequest,
        state: AgentState,
    ) -> InternalRoute:
        injection = assess_prompt_injection(payload.message)
        personal_safety = assess_personal_safety(payload.message)
        if injection.suspected or personal_safety.blocked:
            return InternalRoute.SAFE_RESPONSE

        if needs_routine_goal_clarification(
            payload.message,
            payload.selected_skill,
            [],
        ):
            state["detected_intent"] = "routine_goal_clarification"
            state["intent_confidence"] = 0.98
            state["route_confidence"] = 0.98
            state["route_reason"] = "An ideal routine needs a current objective."
            state["required_context"] = ["active_goals"]
            return InternalRoute.ALFRED

        decision = classify_route(payload.message, payload.selected_skill)
        state["detected_intent"] = decision.detected_intent
        state["intent_confidence"] = decision.confidence
        state["route_confidence"] = decision.confidence
        state["route_reason"] = decision.reason
        if not decision.needs_model:
            return decision.route
        try:
            result = await self._model_gateway.invoke_structured(
                role=ModelRole.ROUTER,
                schema=RoutingDecision,
                system_prompt=build_routing_system_prompt(),
                user_prompt=bounded_json(
                    {
                        "USER_INPUT": payload.message,
                        "selected_skill": payload.selected_skill.value,
                    },
                    max_chars=6_000,
                ),
            )
            if result.parsed.route is InternalRoute.SAFE_RESPONSE:
                return decision.route
            state["token_usage"] = model_usage_update(
                state, result, ModelRole.ROUTER
            )
            state["detected_intent"] = result.parsed.detected_intent
            state["intent_confidence"] = result.parsed.intent_confidence
            state["route_confidence"] = result.parsed.route_confidence
            state["route_reason"] = result.parsed.route_reason
            state["required_context"] = result.parsed.required_context
            return result.parsed.route
        except AIApplicationError as error:
            state["degraded_mode"] = True
            state["fallback_used"] = "deterministic_router_default"
            state["errors"] = [
                {
                    "code": error.code.value,
                    "message": error.message,
                    "component": "router_model",
                }
            ]
            return decision.route

    async def invoke(
        self,
        payload: AIInvokeRequest,
        *,
        is_stream: bool = False,
    ) -> AIInvokeResponse:
        started = perf_counter()
        initial_request_id = uuid4()
        replay = await find_checkpoint_replay(
            self._session,
            user_id=self._user.id,
            idempotency_key=payload.idempotency_key,
        )
        if replay is not None and replay.response:
            _validate_replay_payload(replay, payload)
            return AIInvokeResponse.model_validate(replay.response)

        # Plan validation intentionally precedes even the cheap router model.
        access = await require_active_billing_access(
            self._session,
            self._user.id,
            request_id=initial_request_id,
        )
        if len(payload.message) > access.entitlements.max_input_chars:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "The message exceeds the current plan input limit.",
                request_id=str(initial_request_id),
            )

        conversation = await resolve_conversation(
            self._session,
            user_id=self._user.id,
            conversation_id=payload.conversation_id,
            title_source=payload.message,
        )
        state = AgentState(
            request_id=str(initial_request_id),
            user_id=str(self._user.id),
            conversation_id=str(conversation.id),
            selected_skill=payload.selected_skill,
            original_input=payload.message,
            conversation_summary=conversation.summary_en or "",
            screen_context=payload.screen_context,
            idempotency_key=(
                str(payload.idempotency_key) if payload.idempotency_key else None
            ),
            idempotency_fingerprint=_request_fingerprint(payload),
            token_usage=_token_usage_seed(),
        )
        route = await self._resolve_route(payload, state)
        if route in {
            InternalRoute.RAG_THEN_ALFRED,
            InternalRoute.RAG_THEN_FEEDBACKER,
        } and not access.entitlements.rag_enabled:
            raise AIApplicationError(
                AIErrorCode.PLAN_UNAVAILABLE,
                "RAG is not available on the current plan.",
                request_id=str(initial_request_id),
            )
        state["route"] = route

        reservation = await reserve_ai_usage(
            self._session,
            request_id=initial_request_id,
            user_id=self._user.id,
            route=route,
            timezone_name=self._user.timezone,
            conversation_id=conversation.id,
            idempotency_key=payload.idempotency_key,
            is_stream=is_stream,
        )
        request_id = reservation.event.request_id
        state["request_id"] = str(request_id)
        if reservation.idempotent_replay:
            replay = await find_checkpoint_replay(
                self._session,
                user_id=self._user.id,
                request_id=request_id,
            )
            if replay is not None and replay.response:
                _validate_replay_payload(replay, payload)
                return AIInvokeResponse.model_validate(replay.response)
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "An identical Alfred request is already in progress.",
                request_id=str(request_id),
            )

        expensive_work_started = int(
            state.get("token_usage", {}).get("model_calls", 0)
        ) > 0
        try:
            retriever = (
                await asyncio.to_thread(build_default_knowledge_retriever)
                if route
                in {
                    InternalRoute.RAG_THEN_ALFRED,
                    InternalRoute.RAG_THEN_FEEDBACKER,
                }
                else None
            )
            async with asyncio.timeout(settings.ai_request_timeout_seconds):
                result = dict(
                    await default_graph().ainvoke(
                        state,
                        {"recursion_limit": GRAPH_RECURSION_LIMIT},
                        context=GraphRuntimeContext(
                            session=self._session,
                            authenticated_user_id=self._user.id,
                            model_gateway=self._model_gateway,
                            knowledge_retriever=retriever,
                        ),
                    )
                )
            expensive_work_started = (
                int(result.get("token_usage", {}).get("model_calls", 0)) > 0
                or route
                in {
                    InternalRoute.RAG_THEN_ALFRED,
                    InternalRoute.RAG_THEN_FEEDBACKER,
                }
            )
            final = result["final_response"]
            route = InternalRoute(final["route"])
            usage_data = result.get("token_usage", {})
            await save_message(
                self._session,
                conversation_id=conversation.id,
                user_id=self._user.id,
                role="user",
                content=payload.message,
                request_id=request_id,
                route=route.value,
                detected_language=result.get("detected_language"),
            )
            await save_message(
                self._session,
                conversation_id=conversation.id,
                user_id=self._user.id,
                role="assistant",
                content=str(final["message"]),
                request_id=request_id,
                route=route.value,
                detected_language=result.get("response_language"),
                analysis=_json_safe(final.get("analysis")),
                references=_json_safe(final.get("references", [])),
                proposed_patch=_json_safe(final.get("proposed_patch")),
                requires_confirmation=bool(
                    final.get("requires_confirmation", False)
                ),
                patch_status=(
                    "pending" if final.get("proposed_patch") is not None else None
                ),
            )
            updated_summary = normalize_conversation_summary(
                result.get("summary_update")
            )
            if updated_summary is not None:
                conversation.summary_en = updated_summary
            conversation.updated_at = datetime.now(timezone.utc)
            self._session.add(conversation)
            checkpoint = AIGraphCheckpoint(
                request_id=request_id,
                idempotency_key=payload.idempotency_key,
                user_id=self._user.id,
                conversation_id=conversation.id,
                status=(
                    "pending_confirmation"
                    if final.get("requires_confirmation")
                    else "completed"
                ),
                state=_json_safe(result),
                response={},
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            )
            self._session.add(checkpoint)
            event = await confirm_ai_usage(
                self._session,
                request_id=request_id,
                user_id=self._user.id,
                input_tokens=int(usage_data.get("input_tokens", 0)),
                output_tokens=int(usage_data.get("output_tokens", 0)),
                latency_ms=int((perf_counter() - started) * 1_000),
            )
            snapshot = await get_usage_snapshot(
                self._session,
                user_id=self._user.id,
                timezone_name=self._user.timezone,
            )
            response = AIInvokeResponse(
                request_id=request_id,
                conversation_id=conversation.id,
                route=route,
                message=final["message"],
                references=final.get("references", []),
                analysis=final.get("analysis"),
                proposed_patch=final.get("proposed_patch"),
                requires_confirmation=bool(
                    final.get("requires_confirmation", False)
                ),
                usage=AIUsage(
                    plan=event.plan_code,
                    units_reserved=event.reserved_units,
                    units_consumed=event.consumed_units,
                    units_remaining=snapshot.weighted_units_today.remaining,
                ),
            )
            checkpoint.response = response.model_dump(mode="json")
            self._session.add(checkpoint)
            await self._session.commit()
            return response
        except asyncio.CancelledError:
            await self._session.rollback()
            await release_ai_usage(
                self._session,
                request_id=request_id,
                user_id=self._user.id,
                reason="stream_disconnected",
            )
            raise
        except Exception as exc:
            if not isinstance(exc, (AIApplicationError, asyncio.CancelledError)):
                logger.exception(
                    "Unexpected Alfred graph failure request_id=%s route=%s",
                    request_id,
                    route.value,
                )
            await self._session.rollback()
            try:
                await fail_ai_usage(
                    self._session,
                    request_id=request_id,
                    user_id=self._user.id,
                    reason=(
                        exc.code.value
                        if isinstance(exc, AIApplicationError)
                        else AIErrorCode.GRAPH_EXECUTION_FAILED.value
                    ),
                    charge_reserved_units=expensive_work_started,
                )
            except AIApplicationError:
                pass
            if isinstance(exc, AIApplicationError):
                if exc.request_id is None:
                    exc.request_id = str(request_id)
                raise
            raise AIApplicationError(
                AIErrorCode.GRAPH_EXECUTION_FAILED,
                "Alfred could not complete this request.",
                request_id=str(request_id),
            ) from exc
