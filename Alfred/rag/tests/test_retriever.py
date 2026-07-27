from __future__ import annotations

from dataclasses import dataclass

from Alfred.rag.retriever import (
    RetrievedCandidate,
    TypedRetriever,
    TypedVectorStore,
)
from Alfred.rag.topic_classifier import (
    TopicClassification,
)


def candidate(
    chunk_id: str,
    score: float,
    topic_id: str,
    document_type: str,
    *,
    concept_id: str | None = None,
    related_concept_ids: tuple[str, ...] = (),
) -> RetrievedCandidate:
    return RetrievedCandidate(
        chunk_id=chunk_id,
        score=score,
        content=f"Content for {chunk_id}",
        metadata={
            "chunk_id": chunk_id,
            "document_type": document_type,
            "topic_id": topic_id,
            "concept_id": concept_id,
            "related_concept_ids": list(related_concept_ids),
            "language": "en",
            "status": "machine_audited",
        },
    )


@dataclass
class FakeNamespace:
    candidates: list[RetrievedCandidate]

    @property
    def size(self) -> int:
        return len(self.candidates)

    def search_candidates(
        self,
        query_vector: list[float],
        limit: int,
    ) -> list[RetrievedCandidate]:
        return self.candidates[:limit]


class FakeEmbedder:
    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0]


class NoMatchLexicalClassifier:
    def classify(self, query: str) -> TopicClassification:
        return TopicClassification(
            topic_id=None,
            confidence="low",
            score=0,
            matched_terms=(),
        )


def build_fake_store() -> TypedVectorStore:
    knowledge = FakeNamespace(
        candidates=[
            candidate(
                "chunk-procrastination",
                0.82,
                "procrastination",
                "knowledge",
                concept_id="procrastination-pattern",
            ),
            candidate(
                "chunk-planning",
                0.71,
                "planning",
                "knowledge",
                concept_id="action-planning",
            ),
            candidate(
                "chunk-motivation",
                0.62,
                "motivation",
                "knowledge",
                concept_id="motivation-variability",
            ),
        ]
    )
    playbooks = FakeNamespace(
        candidates=[
            candidate(
                "chunk-playbook-cannot-start",
                0.79,
                "procrastination",
                "playbook",
                related_concept_ids=("procrastination-pattern",),
            )
        ]
    )

    return TypedVectorStore(
        knowledge=knowledge,  # type: ignore[arg-type]
        playbooks=playbooks,  # type: ignore[arg-type]
    )


def test_uses_semantic_fallback_when_lexical_topic_is_missing():
    retriever = TypedRetriever(
        vector_store=build_fake_store(),
        topic_classifier=NoMatchLexicalClassifier(),  # type: ignore[arg-type]
        embedder=FakeEmbedder(),  # type: ignore[arg-type]
    )

    result = retriever.retrieve(
        "Whenever I need to write, I organize folders instead."
    )

    assert result.topic_id == "procrastination"
    assert result.topic_confidence == "high"
    assert result.topic_source == "semantic"
    assert result.topic_decision_reason == "semantic_match"
    assert result.topic_candidates[0].topic_id == "procrastination"
    assert result.playbook is not None
    assert result.playbook.chunk_id == "chunk-playbook-cannot-start"
    assert [item.chunk_id for item in result.knowledge] == [
        "chunk-procrastination"
    ]


def test_semantic_fallback_rejects_an_ambiguous_topic():
    decision = TypedRetriever._infer_semantic_topic(
        candidates=[
            candidate(
                "chunk-procrastination",
                0.52,
                "procrastination",
                "knowledge",
            ),
            candidate(
                "chunk-planning",
                0.50,
                "planning",
                "knowledge",
            ),
        ]
    )

    assert decision.topic_id is None
    assert decision.confidence == "low"
    assert decision.reason == "ambiguous"
    assert decision.margin < 0.03
    assert [item.topic_id for item in decision.candidates] == [
        "procrastination",
        "planning",
    ]


def test_retrieval_result_exposes_ambiguous_topic_candidates():
    store = TypedVectorStore(
        knowledge=FakeNamespace(  # type: ignore[arg-type]
            candidates=[
                candidate(
                    "chunk-procrastination",
                    0.52,
                    "procrastination",
                    "knowledge",
                ),
                candidate(
                    "chunk-planning",
                    0.50,
                    "planning",
                    "knowledge",
                ),
            ]
        ),
        playbooks=FakeNamespace(candidates=[]),  # type: ignore[arg-type]
    )
    retriever = TypedRetriever(
        vector_store=store,
        topic_classifier=NoMatchLexicalClassifier(),  # type: ignore[arg-type]
        embedder=FakeEmbedder(),  # type: ignore[arg-type]
    )

    result = retriever.retrieve("A semantically ambiguous query.")

    assert result.topic_id is None
    assert result.topic_source == "none"
    assert result.topic_decision_reason == "ambiguous"
    assert [item.topic_id for item in result.topic_candidates] == [
        "procrastination",
        "planning",
    ]
    assert result.playbook is None
    assert result.knowledge == ()
    assert result.retrieval_warnings == (
        "Topic classification is ambiguous.",
    )
