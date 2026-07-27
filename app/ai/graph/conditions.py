"""Pure conditional-edge functions for the unified graph.

They are async even though they do no I/O. With the installed LangGraph and
Python 3.14, synchronous conditions are dispatched to a thread executor during
``ainvoke``; async conditions keep the entire request graph on the event loop
and shut down cleanly.
"""

from typing import Literal

from app.ai.domain.enums import InternalRoute, PatchDecision
from app.ai.graph.state import AgentState

SafetyBranch = Literal["allowed", "blocked"]
RetrievalBranch = Literal["sufficient", "insufficient"]
CriticBranch = Literal["critic", "skip"]
ApprovalBranch = Literal["approved", "revise"]
PatchBranch = Literal["patch", "no_patch"]
PatchSafetyBranch = Literal["safe", "unsafe"]
HumanBranch = Literal["accepted", "rejected", "edited", "pending"]
MemoryBranch = Literal["store", "skip"]
MainRouteBranch = Literal[
    "safe_response",
    "deterministic",
    "alfred",
    "feedbacker",
    "rag_then_alfred",
    "rag_then_feedbacker",
]


async def route_after_safety(state: AgentState) -> SafetyBranch:
    return "blocked" if state.get("blocked", False) else "allowed"


async def route_main_capability(state: AgentState) -> MainRouteBranch:
    route = state.get("route", InternalRoute.SAFE_RESPONSE)
    normalized = route if isinstance(route, InternalRoute) else InternalRoute(route)
    # Path keys are plain strings so graph topology is independent from the
    # enum implementation used in the serializable state.
    return normalized.value


async def route_after_retrieval_validation(state: AgentState) -> RetrievalBranch:
    return "insufficient" if state.get("insufficient_evidence", True) else "sufficient"


async def route_after_rag(
    state: AgentState,
) -> Literal["alfred", "feedbacker"]:
    route = state.get("route", InternalRoute.RAG_THEN_ALFRED)
    normalized = route if isinstance(route, InternalRoute) else InternalRoute(route)
    if normalized is InternalRoute.RAG_THEN_FEEDBACKER:
        return "feedbacker"
    return "alfred"


async def route_critic_requirement(state: AgentState) -> CriticBranch:
    return "critic" if state.get("critic_required", False) else "skip"


async def route_critic_approval(state: AgentState) -> ApprovalBranch:
    output = state.get("critic_output", {})
    return "approved" if output.get("approved", False) else "revise"


async def route_patch_presence(state: AgentState) -> PatchBranch:
    return "patch" if state.get("proposed_patch") is not None else "no_patch"


async def route_patch_safety(state: AgentState) -> PatchSafetyBranch:
    validation = state.get("patch_validation", {})
    return (
        "safe"
        if validation.get("valid", False) and validation.get("safe", False)
        else "unsafe"
    )


async def route_human_decision(state: AgentState) -> HumanBranch:
    decision = state.get("human_decision")
    if decision is None:
        return "pending"
    normalized = (
        decision if isinstance(decision, PatchDecision) else PatchDecision(decision)
    )
    return normalized.value


async def route_memory_decision(state: AgentState) -> MemoryBranch:
    candidates = state.get("memories_to_store", state.get("memory_candidates", []))
    return "store" if candidates else "skip"
