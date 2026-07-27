"""Curated, multilingual retrieval infrastructure for the unified AI graph.

Heavy embedding dependencies are intentionally not imported here. Production
composition is available from ``app.ai.retrieval.runtime`` and remains lazy so
ordinary API routes do not load PyTorch.
"""
