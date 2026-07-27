"""Compatibility import for the pre-application graph module.

New code must import :class:`AgentState` from ``app.ai.graph.state``. This
module remains temporarily so unfinished local prototypes do not break while
the graph is migrated stage by stage.
"""

from app.ai.graph.state import AgentState

__all__ = ["AgentState"]
