"""Audit-friendly RAG contracts."""

from typing import Any

from pydantic import Field

from app.ai.schemas.base import AISchema


class RetrievedDocument(AISchema):
    document_id: str = Field(min_length=1, max_length=200)
    chunk_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=12_000)
    source: str = Field(min_length=1, max_length=1_000)
    topic: str | None = Field(default=None, max_length=100)
    retrieval_score: float = Field(ge=0, le=1)
    rerank_score: float | None = Field(default=None, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceReference(AISchema):
    source_id: str | None = Field(default=None, min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=300)
    authors: list[str] = Field(default_factory=list, max_length=30)
    publication_year: int | None = Field(default=None, ge=1_000, le=3_000)
    url: str | None = Field(default=None, max_length=2_000)
    doi: str | None = Field(default=None, max_length=300)

    # Nullable legacy fields keep old persisted assistant messages readable.
    document_id: str | None = Field(default=None, min_length=1, max_length=200)
    chunk_id: str | None = Field(default=None, min_length=1, max_length=200)
    source: str | None = Field(default=None, min_length=1, max_length=1_000)
    source_ids: list[str] = Field(default_factory=list, max_length=20)
    topic: str | None = Field(default=None, max_length=100)
    supporting_excerpt: str | None = Field(default=None, max_length=1_000)
    retrieval_score: float | None = Field(default=None, ge=0, le=1)
    rerank_score: float | None = Field(default=None, ge=0, le=1)


class EvidencePack(AISchema):
    query: str = Field(min_length=1, max_length=2_000)
    topics: list[str] = Field(default_factory=list, max_length=20)
    references: list[EvidenceReference] = Field(default_factory=list, max_length=12)
    evidence_items: list[dict[str, Any]] = Field(default_factory=list, max_length=12)
    confidence: float = Field(ge=0, le=1)
    coverage: float = Field(ge=0, le=1)
    insufficient_evidence: bool = False
    trust_boundary: str = Field(min_length=1, max_length=100)
