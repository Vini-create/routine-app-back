"""Legacy module for Alfred's internal analytical capability.

Feedbacker is not a public agent. Its graph nodes will be implemented in
``app.ai.graph.nodes.analysis`` while structured contracts already live in
``app.ai.schemas.analysis``.
"""

from app.ai.schemas.analysis import AnalysisReport

__all__ = ["AnalysisReport"]
