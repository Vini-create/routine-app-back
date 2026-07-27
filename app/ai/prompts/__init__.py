"""Versioned prompt contracts for model-backed Alfred capabilities."""

from app.ai.prompts.alfred import build_alfred_system_prompt
from app.ai.prompts.analysis import build_feedbacker_system_prompt
from app.ai.prompts.routing import build_routing_system_prompt

__all__ = [
    "build_alfred_system_prompt",
    "build_feedbacker_system_prompt",
    "build_routing_system_prompt",
]
