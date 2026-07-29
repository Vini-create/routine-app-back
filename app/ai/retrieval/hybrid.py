"""Dense + BM25 retrieval with deterministic reciprocal-rank fusion."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np
from langchain_core.embeddings import Embeddings

from app.ai.retrieval.corpus import CorpusChunk

TOKEN_PATTERN = re.compile(r"\b[\w-]{2,}\b", re.UNICODE)
RRF_K = 60


def lexical_tokens(value: str) -> tuple[str, ...]:
    folded = unicodedata.normalize("NFKC", value).casefold()
    return tuple(TOKEN_PATTERN.findall(folded))


@dataclass(frozen=True, slots=True)
class RetrievalCandidate:
    chunk: CorpusChunk
    dense_score: float
    lexical_score: float
    fusion_score: float
    dense_rank: int | None
    lexical_rank: int | None

    def to_document(self) -> dict[str, object]:
        metadata = self.chunk.to_metadata()
        metadata["dense_rank"] = self.dense_rank
        metadata["lexical_rank"] = self.lexical_rank
        metadata["dense_score"] = round(self.dense_score, 6)
        metadata["lexical_score"] = round(self.lexical_score, 6)
        metadata["fusion_score"] = round(self.fusion_score, 6)
        return {
            "document_id": self.chunk.document_id,
            "chunk_id": self.chunk.chunk_id,
            "title": self.chunk.title,
            "content": self.chunk.content,
            "source": self.chunk.source_path,
            "topic": self.chunk.topic_id,
            "retrieval_score": round(self.fusion_score, 6),
            "metadata": metadata,
        }


@runtime_checkable
class KnowledgeRetriever(Protocol):
    def retrieve(self, query: str, *, limit: int = 12) -> list[dict[str, object]]:
        """Return bounded, ranked candidate dictionaries."""

    async def aretrieve(
        self,
        query: str,
        *,
        limit: int = 12,
    ) -> list[dict[str, object]]:
        """Async boundary used by LangGraph request nodes."""


class BM25Index:
    """Small in-memory BM25 implementation for the curated static corpus."""

    def __init__(self, documents: tuple[CorpusChunk, ...]) -> None:
        self._token_counts = tuple(
            Counter(
                lexical_tokens(
                    " ".join(
                        (
                            document.title,
                            document.topic_id,
                            document.concept_id or "",
                            *document.related_concept_ids,
                            document.content,
                        )
                    )
                )
            )
            for document in documents
        )
        self._lengths = tuple(sum(counts.values()) for counts in self._token_counts)
        self._average_length = (
            sum(self._lengths) / len(self._lengths) if self._lengths else 0.0
        )
        document_frequency: Counter[str] = Counter()
        for counts in self._token_counts:
            document_frequency.update(counts.keys())
        total = len(documents)
        self._idf = {
            term: math.log(1.0 + (total - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def scores(self, query: str) -> np.ndarray:
        query_terms = lexical_tokens(query)
        scores = np.zeros(len(self._token_counts), dtype=np.float32)
        if not query_terms or self._average_length == 0:
            return scores
        k1 = 1.5
        b = 0.75
        for index, counts in enumerate(self._token_counts):
            document_length = self._lengths[index]
            score = 0.0
            for term in query_terms:
                frequency = counts.get(term, 0)
                if not frequency:
                    continue
                denominator = frequency + k1 * (
                    1 - b + b * document_length / self._average_length
                )
                score += self._idf.get(term, 0.0) * (
                    frequency * (k1 + 1) / denominator
                )
            scores[index] = score
        return scores


class HybridKnowledgeRetriever:
    """Retrieve public curated evidence without reading any user's records."""

    def __init__(
        self,
        *,
        documents: tuple[CorpusChunk, ...],
        embeddings: Embeddings,
        document_vectors: np.ndarray | None = None,
        candidate_pool: int = 16,
    ) -> None:
        if not documents:
            raise ValueError("The knowledge retriever requires a non-empty corpus.")
        if candidate_pool < 4:
            raise ValueError("candidate_pool must be at least 4.")
        self._documents = documents
        self._embeddings = embeddings
        self._candidate_pool = min(candidate_pool, len(documents))
        vectors = (
            np.asarray(document_vectors, dtype=np.float32)
            if document_vectors is not None
            else np.asarray(
                embeddings.embed_documents(
                    [document.content for document in documents]
                ),
                dtype=np.float32,
            )
        )
        if vectors.ndim != 2 or vectors.shape[0] != len(documents):
            raise ValueError("The embedding matrix does not match the corpus.")
        if not np.isfinite(vectors).all():
            raise ValueError("The embedding matrix contains non-finite values.")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("The embedding matrix contains a zero vector.")
        self._dense_matrix = vectors / norms
        self._bm25 = BM25Index(documents)

    def retrieve(self, query: str, *, limit: int = 12) -> list[dict[str, object]]:
        query = query.strip()
        if not query:
            raise ValueError("The retrieval query cannot be empty.")
        if not 1 <= limit <= 50:
            raise ValueError("The retrieval limit must be between 1 and 50.")

        vector = np.asarray(self._embeddings.embed_query(query), dtype=np.float32)
        if vector.ndim != 1 or vector.shape[0] != self._dense_matrix.shape[1]:
            raise ValueError("The query embedding dimension differs from the corpus.")
        norm = float(np.linalg.norm(vector))
        if not math.isfinite(norm) or norm == 0:
            raise ValueError("The query embedding is invalid.")
        dense_scores = self._dense_matrix @ (vector / norm)
        lexical_scores = self._bm25.scores(query)

        pool = self._candidate_pool
        dense_order = np.argsort(-dense_scores, kind="stable")[:pool]
        lexical_order = np.argsort(-lexical_scores, kind="stable")[:pool]
        dense_ranks = {int(index): rank for rank, index in enumerate(dense_order, 1)}
        lexical_ranks = {
            int(index): rank
            for rank, index in enumerate(lexical_order, 1)
            if lexical_scores[index] > 0
        }
        candidate_indexes = set(dense_ranks) | set(lexical_ranks)
        maximum_rrf = 2 / (RRF_K + 1)

        candidates: list[RetrievalCandidate] = []
        for index in candidate_indexes:
            dense_rank = dense_ranks.get(index)
            lexical_rank = lexical_ranks.get(index)
            rrf = 0.0
            if dense_rank is not None:
                rrf += 1 / (RRF_K + dense_rank)
            if lexical_rank is not None:
                rrf += 1 / (RRF_K + lexical_rank)
            candidates.append(
                RetrievalCandidate(
                    chunk=self._documents[index],
                    dense_score=float(dense_scores[index]),
                    lexical_score=float(lexical_scores[index]),
                    fusion_score=rrf / maximum_rrf,
                    dense_rank=dense_rank,
                    lexical_rank=lexical_rank,
                )
            )

        candidates.sort(
            key=lambda item: (
                item.fusion_score,
                item.dense_score,
                item.lexical_score,
                item.chunk.chunk_id,
            ),
            reverse=True,
        )
        return [candidate.to_document() for candidate in candidates[:limit]]

    async def aretrieve(
        self,
        query: str,
        *,
        limit: int = 12,
    ) -> list[dict[str, object]]:
        # Query embedding and ranking are synchronous. Offloading keeps
        # concurrent FastAPI/LangGraph requests from blocking the event loop.
        import asyncio

        return await asyncio.to_thread(self.retrieve, query, limit=limit)
