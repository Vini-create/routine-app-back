"""Legacy module for Alfred's former standalone prototype.

Alfred is now the single public AI experience orchestrated from ``app.ai``.
Conversational nodes will be implemented in
``app.ai.graph.nodes.conversation``. The existing RAG corpus and retrieval
utilities remain under ``Alfred.rag`` until their staged migration.
"""

from app.ai.schemas.alfred import AlfredIntervention, AlfredResponsePlan

__all__ = ["AlfredIntervention", "AlfredResponsePlan"]
