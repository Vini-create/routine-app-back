"""Pydantic contracts for Alfred's unified public and internal APIs."""

from app.ai.schemas.requests import AIInvokeRequest
from app.ai.schemas.responses import AIInvokeResponse

__all__ = ["AIInvokeRequest", "AIInvokeResponse"]
