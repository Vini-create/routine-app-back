"""Legacy import path for Alfred's unified contracts.

The RAG prototype still lives in ``Alfred/`` while it is migrated. Public API
code must use ``app.ai.schemas`` directly.
"""

from app.ai.schemas.alfred import AlfredIntervention, AlfredResponsePlan
from app.ai.schemas.requests import AIInvokeRequest
from app.ai.schemas.responses import AIInvokeResponse

__all__ = [
    "AIInvokeRequest",
    "AIInvokeResponse",
    "AlfredIntervention",
    "AlfredResponsePlan",
]
