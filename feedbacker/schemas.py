"""Legacy import path for Alfred's internal analytical contracts.

Feedbacker is not a separate public request or response. The name remains only
as an internal implementation boundary until its code is migrated to
``app.ai.graph.nodes.analysis``.
"""

from app.ai.schemas.analysis import (
    AnalysisReport,
    ExecutionDiagnosis,
    IdentifiedPattern,
    Recommendation,
    RootCauseHypothesis,
    SuccessMetric,
)
from app.ai.schemas.patches import PatchOperation, ProposedPatch

__all__ = [
    "AnalysisReport",
    "ExecutionDiagnosis",
    "IdentifiedPattern",
    "PatchOperation",
    "ProposedPatch",
    "Recommendation",
    "RootCauseHypothesis",
    "SuccessMetric",
]
