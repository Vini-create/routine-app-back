"""Safe proposal, simulation and human-confirmed patch application."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.schemas.patches import PatchOperation, ProposedPatch
from app.ai.repositories.persistence_repository import (
    record_feedbacker_decision_memory,
)
from app.models.ai import (
    AIGraphCheckpoint,
    AIMessage,
    AIPatchAudit,
    AIProposedPatch,
)
from app.models.routine import CoachProfile, Goal, Habit, RoutineItem
from app.schemas.routine_schemas import (
    CoachProfileUpdate,
    GoalUpdate,
    HabitUpdate,
    RoutineItemUpdate,
)

PATCH_TTL = timedelta(hours=24)

_ENTITY_CONFIG: dict[str, tuple[type[Any], type[Any], frozenset[str]]] = {
    "goal": (
        Goal,
        GoalUpdate,
        frozenset({"title", "description", "category", "target_date"}),
    ),
    "habit": (
        Habit,
        HabitUpdate,
        frozenset(
            {
                "goal_id",
                "name",
                "description",
                "duration_minutes",
                "recurrence_rule",
                "start_date",
            }
        ),
    ),
    "routine_item": (
        RoutineItem,
        RoutineItemUpdate,
        frozenset(
            {
                "goal_id",
                "title",
                "description",
                "item_type",
                "schedule_type",
                "start_at",
                "end_at",
                "duration_minutes",
                "recurrence_rule",
            }
        ),
    ),
    "profile": (
        CoachProfile,
        CoachProfileUpdate,
        frozenset({"name", "style", "description"}),
    ),
}


@dataclass(frozen=True, slots=True)
class PatchSimulation:
    entity: Any
    before: dict[str, Any]
    after: dict[str, Any]
    normalized_values: dict[str, Any]

    def public(self) -> dict[str, Any]:
        return {
            "status": "validated",
            "before": _json_safe(self.before),
            "after": _json_safe(self.after),
            "changed_fields": sorted(self.normalized_values),
        }


def _now(value: datetime | None = None) -> datetime:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return current


def _json_safe(value: Any) -> Any:
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _entity_state(entity: Any, fields: frozenset[str]) -> dict[str, Any]:
    return {field: getattr(entity, field) for field in sorted(fields)}


async def _owned_entity(
    session: AsyncSession,
    *,
    user_id: UUID,
    entity_type: str,
    entity_id: UUID | None,
    for_update: bool,
) -> Any:
    config = _ENTITY_CONFIG.get(entity_type)
    if config is None or entity_id is None:
        raise AIApplicationError(
            AIErrorCode.INVALID_REQUEST,
            "A supported entity_type and entity_id are required for a patch.",
        )
    model = config[0]
    statement = select(model).where(model.id == entity_id)
    if for_update:
        statement = statement.with_for_update()
    result = await session.execute(statement)
    entity = result.scalar_one_or_none()
    if entity is None:
        raise AIApplicationError(
            AIErrorCode.PATCH_NOT_FOUND,
            "The entity selected by the patch was not found.",
        )
    if entity.user_id != user_id:
        raise AIApplicationError(
            AIErrorCode.PATCH_FORBIDDEN,
            "The patch cannot access another user's entity.",
        )
    return entity


async def validate_and_simulate_patch(
    session: AsyncSession,
    *,
    user_id: UUID,
    patch: ProposedPatch,
    for_update: bool = False,
) -> PatchSimulation:
    """Validate ownership, allowlisted fields and the entity's own schema."""

    model, update_schema, allowed_fields = _ENTITY_CONFIG[patch.entity_type]
    del model
    entity = await _owned_entity(
        session,
        user_id=user_id,
        entity_type=patch.entity_type,
        entity_id=patch.entity_id,
        for_update=for_update,
    )
    before = _entity_state(entity, allowed_fields)
    raw_updates: dict[str, Any] = {}
    for operation in patch.operations:
        parts = operation.path.removeprefix("/").split("/")
        if len(parts) != 1 or parts[0] not in allowed_fields:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                f"Patch path '{operation.path}' is not editable.",
            )
        field = parts[0]
        if field in raw_updates:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                f"Patch path '{operation.path}' is duplicated.",
            )
        if operation.op == "remove":
            raw_updates[field] = None
        else:
            raw_updates[field] = operation.value

    try:
        normalized = update_schema.model_validate(raw_updates).model_dump(
            exclude_unset=True
        )
    except ValidationError as exc:
        raise AIApplicationError(
            AIErrorCode.INVALID_REQUEST,
            "The proposed values violate the entity schema.",
        ) from exc

    goal_id = normalized.get("goal_id")
    if goal_id is not None:
        goal = await session.get(Goal, goal_id)
        if goal is None or goal.user_id != user_id:
            raise AIApplicationError(
                AIErrorCode.PATCH_FORBIDDEN,
                "A patch cannot link an entity to another user's goal.",
            )

    after = {**before, **normalized}
    if isinstance(entity, RoutineItem):
        if after["end_at"] is not None and after["end_at"] <= after["start_at"]:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "The simulated routine end must be after its start.",
            )
        if after["schedule_type"] == "recurring" and not after["recurrence_rule"]:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "A recurring routine item requires a recurrence rule.",
            )
        if after["schedule_type"] == "single" and after["recurrence_rule"]:
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "A single routine item cannot keep a recurrence rule.",
            )

    return PatchSimulation(
        entity=entity,
        before=before,
        after=after,
        normalized_values=normalized,
    )


async def persist_pending_patch(
    session: AsyncSession,
    *,
    request_id: UUID,
    user_id: UUID,
    conversation_id: UUID,
    patch: ProposedPatch,
    simulation: PatchSimulation,
    now: datetime | None = None,
) -> AIProposedPatch:
    persisted = AIProposedPatch(
        request_id=request_id,
        user_id=user_id,
        conversation_id=conversation_id,
        status="pending",
        entity_type=patch.entity_type,
        entity_id=patch.entity_id,
        operations=[
            operation.model_dump(mode="json") for operation in patch.operations
        ],
        reason=patch.reason,
        simulation=simulation.public(),
        success_metrics=patch.success_metrics,
        expires_at=_now(now) + PATCH_TTL,
    )
    session.add(persisted)
    await session.flush()
    return persisted


async def _owned_patch_for_update(
    session: AsyncSession,
    *,
    patch_id: UUID,
    user_id: UUID,
    now: datetime,
) -> AIProposedPatch:
    result = await session.execute(
        select(AIProposedPatch)
        .where(AIProposedPatch.id == patch_id)
        .with_for_update()
    )
    patch = result.scalar_one_or_none()
    if patch is None:
        raise AIApplicationError(AIErrorCode.PATCH_NOT_FOUND, "Patch not found.")
    if patch.user_id != user_id:
        raise AIApplicationError(
            AIErrorCode.PATCH_FORBIDDEN,
            "The patch belongs to another user.",
        )
    if patch.status == "pending" and patch.expires_at <= now:
        patch.status = "expired"
        session.add(patch)
        await _sync_assistant_patch_message(
            session,
            patch=patch,
            status="expired",
        )
        await session.commit()
        raise AIApplicationError(
            AIErrorCode.PATCH_EXPIRED,
            "The patch confirmation window has expired.",
        )
    return patch


def _public_patch(patch: AIProposedPatch) -> ProposedPatch:
    return ProposedPatch.model_validate(
        {
            "patch_id": patch.id,
            "entity_type": patch.entity_type,
            "entity_id": patch.entity_id,
            "operations": [
                PatchOperation.model_validate(item) for item in patch.operations
            ],
            "reason": patch.reason,
            "simulation": patch.simulation,
            "success_metrics": patch.success_metrics,
        }
    )


async def _sync_assistant_patch_message(
    session: AsyncSession,
    *,
    patch: AIProposedPatch,
    status: str,
    refresh_proposed_patch: bool = False,
) -> None:
    """Keep the owned assistant artifact aligned with its persisted patch."""

    message = await session.scalar(
        select(AIMessage)
        .where(
            AIMessage.request_id == patch.request_id,
            AIMessage.conversation_id == patch.conversation_id,
            AIMessage.user_id == patch.user_id,
            AIMessage.role == "assistant",
        )
        .with_for_update()
    )
    if message is None:
        # Patches created before unified message persistence remain resolvable.
        return
    message.patch_status = status
    message.requires_confirmation = status == "pending"
    if refresh_proposed_patch:
        message.proposed_patch = _public_patch(patch).model_dump(mode="json")
    session.add(message)


async def accept_patch(
    session: AsyncSession,
    *,
    patch_id: UUID,
    user_id: UUID,
    idempotency_key: UUID,
    now: datetime | None = None,
) -> tuple[AIProposedPatch, AIPatchAudit]:
    current = _now(now)
    try:
        patch = await _owned_patch_for_update(
            session, patch_id=patch_id, user_id=user_id, now=current
        )
        if patch.status == "applied":
            if patch.resolution_idempotency_key == idempotency_key:
                audit = await session.scalar(
                    select(AIPatchAudit).where(
                        AIPatchAudit.patch_id == patch.id,
                        AIPatchAudit.action == "applied",
                    )
                )
                if audit is not None:
                    await _sync_assistant_patch_message(
                        session,
                        patch=patch,
                        status="applied",
                    )
                    await session.commit()
                    return patch, audit
            raise AIApplicationError(
                AIErrorCode.PATCH_ALREADY_RESOLVED,
                "The patch has already been applied.",
            )
        if patch.status != "pending":
            raise AIApplicationError(
                AIErrorCode.PATCH_ALREADY_RESOLVED,
                "The patch is no longer pending.",
            )

        public_patch = _public_patch(patch)
        simulation = await validate_and_simulate_patch(
            session,
            user_id=user_id,
            patch=public_patch,
            for_update=True,
        )
        for field, value in simulation.normalized_values.items():
            setattr(simulation.entity, field, value)
        patch.status = "applied"
        patch.applied_at = current
        patch.resolution_idempotency_key = idempotency_key
        await _sync_assistant_patch_message(
            session,
            patch=patch,
            status="applied",
        )
        audit = AIPatchAudit(
            patch_id=patch.id,
            user_id=user_id,
            action="applied",
            before_state=_json_safe(simulation.before),
            after_state=_json_safe(simulation.after),
            rollback_payload={
                "entity_type": patch.entity_type,
                "entity_id": str(patch.entity_id),
                "values": _json_safe(simulation.before),
            },
        )
        session.add_all([simulation.entity, patch, audit])
        await record_feedbacker_decision_memory(
            session,
            patch=patch,
            decision="accepted",
            reason=None,
            created_at=current,
        )
        checkpoint = await session.scalar(
            select(AIGraphCheckpoint)
            .where(AIGraphCheckpoint.request_id == patch.request_id)
            .with_for_update()
        )
        if checkpoint is not None:
            checkpoint.status = "resolved"
            session.add(checkpoint)

        await session.commit()
        await session.refresh(patch)
        await session.refresh(audit)
        return patch, audit
    except AIApplicationError:
        await session.rollback()
        raise


async def reject_patch(
    session: AsyncSession,
    *,
    patch_id: UUID,
    user_id: UUID,
    reason: str | None,
    now: datetime | None = None,
) -> tuple[AIProposedPatch, AIPatchAudit]:
    current = _now(now)
    try:
        patch = await _owned_patch_for_update(
            session, patch_id=patch_id, user_id=user_id, now=current
        )
        if patch.status != "pending":
            raise AIApplicationError(
                AIErrorCode.PATCH_ALREADY_RESOLVED,
                "The patch is no longer pending.",
            )
        patch.status = "rejected"
        patch.rejected_at = current
        await _sync_assistant_patch_message(
            session,
            patch=patch,
            status="rejected",
        )
        audit = AIPatchAudit(
            patch_id=patch.id,
            user_id=user_id,
            action="rejected",
            before_state=patch.simulation.get("before", {}),
            after_state=patch.simulation.get("before", {}),
            rollback_payload={"reason": reason},
        )
        session.add_all([patch, audit])
        await record_feedbacker_decision_memory(
            session,
            patch=patch,
            decision="rejected",
            reason=reason,
            created_at=current,
        )
        checkpoint = await session.scalar(
            select(AIGraphCheckpoint)
            .where(AIGraphCheckpoint.request_id == patch.request_id)
            .with_for_update()
        )
        if checkpoint is not None:
            checkpoint.status = "resolved"
            session.add(checkpoint)
        await session.commit()
        await session.refresh(patch)
        await session.refresh(audit)
        return patch, audit
    except AIApplicationError:
        await session.rollback()
        raise


async def edit_patch(
    session: AsyncSession,
    *,
    patch_id: UUID,
    user_id: UUID,
    idempotency_key: UUID,
    operations: list[PatchOperation],
    now: datetime | None = None,
) -> AIProposedPatch:
    current = _now(now)
    try:
        patch = await _owned_patch_for_update(
            session, patch_id=patch_id, user_id=user_id, now=current
        )
        if patch.status != "pending":
            raise AIApplicationError(
                AIErrorCode.PATCH_ALREADY_RESOLVED,
                "The patch is no longer pending.",
            )
        serialized_operations = [
            operation.model_dump(mode="json") for operation in operations
        ]
        if patch.resolution_idempotency_key == idempotency_key:
            if patch.operations == serialized_operations:
                await _sync_assistant_patch_message(
                    session,
                    patch=patch,
                    status="pending",
                    refresh_proposed_patch=True,
                )
                await session.commit()
                return patch
            raise AIApplicationError(
                AIErrorCode.INVALID_REQUEST,
                "The edit idempotency key was reused with different operations.",
            )
        candidate = _public_patch(patch).model_copy(
            update={"operations": operations, "patch_id": patch.id}
        )
        simulation = await validate_and_simulate_patch(
            session, user_id=user_id, patch=candidate
        )
        previous_simulation = dict(patch.simulation)
        previous_operations = list(patch.operations)
        patch.operations = serialized_operations
        patch.simulation = simulation.public()
        patch.resolution_idempotency_key = idempotency_key
        await _sync_assistant_patch_message(
            session,
            patch=patch,
            status="pending",
            refresh_proposed_patch=True,
        )
        session.add_all(
            [
                patch,
                AIPatchAudit(
                    patch_id=patch.id,
                    user_id=user_id,
                    action="edited",
                    before_state=previous_simulation.get("after", {}),
                    after_state=patch.simulation.get("after", {}),
                    rollback_payload={
                        "operations": previous_operations
                    },
                ),
            ]
        )
        await session.commit()
        await session.refresh(patch)
        return patch
    except AIApplicationError:
        await session.rollback()
        raise


def public_patch(patch: AIProposedPatch) -> ProposedPatch:
    return _public_patch(patch)
