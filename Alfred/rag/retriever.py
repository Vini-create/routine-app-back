from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import faiss
import numpy as np

from Alfred.rag.embeddings import OpenAIEmbedder
from Alfred.rag.paths import INDEX_DIR
from Alfred.rag.topic_classifier import (
    LexicalTopicClassifier,
)

INDEX_MANIFEST_PATH = INDEX_DIR / "manifest.json"


@dataclass(frozen=True)
class RetrievedCandidate:
    chunk_id: str
    score: float
    content: str
    metadata: dict[str, Any]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    # O FAISS armazena apenas vetores. Este JSONL paralelo recupera o conteúdo
    # e os metadados do chunk preservando a mesma ordem dos vetores.
    records: list[dict[str, Any]] = []

    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}."
                ) from error

            records.append(record)

    return records


class FaissNamespace:
    def __init__(
        self,
        name: str,
        index: faiss.Index,
        records: list[dict[str, Any]],
    ) -> None:
        self.name = name
        self.index = index
        self.records = records

        # O FAISS retorna posições numéricas. Se as quantidades divergissem,
        # uma posição poderia apontar para os metadados do chunk errado.
        if self.index.ntotal != len(self.records):
            raise ValueError(
                f"Index '{name}' has {self.index.ntotal} vectors, "
                f"but {len(self.records)} metadata records."
            )

    @property
    def dimension(self) -> int:
        return self.index.d

    @property
    def size(self) -> int:
        return self.index.ntotal

    def search_candidates(
        self,
        query_vector: list[float],
        limit: int,
    ) -> list[RetrievedCandidate]:
        if limit < 1:
            raise ValueError("Search limit must be at least 1.")

        query_matrix = np.asarray(
            [query_vector],
            dtype=np.float32,
        )

        if query_matrix.shape != (1, self.dimension):
            raise ValueError(
                f"Query vector must have {self.dimension} dimensions."
            )

        # Os vetores dos documentos foram normalizados ao criar o índice. A
        # consulta também precisa ser normalizada para que o produto interno
        # calculado pelo FAISS equivalha à similaridade de cosseno.
        faiss.normalize_L2(query_matrix)

        # Esta é a busca nativa do FAISS. Ela devolve posições e scores de
        # similaridade, não os IDs dos chunks ou seus textos.
        scores, positions = self.index.search(query_matrix, limit)

        candidates: list[RetrievedCandidate] = []

        for score, position in zip(scores[0], positions[0], strict=True):
            if position == -1:
                continue

            # A posição retornada pelo FAISS aponta diretamente para a mesma
            # linha/registro do JSONL paralelo carregado acima.
            record = self.records[position]

            candidates.append(
                RetrievedCandidate(
                    chunk_id=record["chunk_id"],
                    score=float(score),
                    content=record["content"],
                    metadata=record["metadata"],
                )
            )

        return candidates


@dataclass(frozen=True)
class TypedVectorStore:
    # Playbooks e conhecimento científico permanecem em namespaces separados
    # porque cada tipo segue regras diferentes no contrato de recuperação.
    knowledge: FaissNamespace
    playbooks: FaissNamespace


def load_vector_store() -> TypedVectorStore:
    if not INDEX_MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            "FAISS index manifest was not found. "
            "Run the index build first."
        )

    manifest = json.loads(
        INDEX_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    namespaces: dict[str, FaissNamespace] = {}

    for name, details in manifest["indexes"].items():
        index_path = INDEX_DIR / details["index_file"]
        metadata_path = INDEX_DIR / details["metadata_file"]

        if not index_path.is_file():
            raise FileNotFoundError(f"Missing FAISS index: {index_path}")

        if not metadata_path.is_file():
            raise FileNotFoundError(
                f"Missing metadata sidecar: {metadata_path}"
            )

        namespaces[name] = FaissNamespace(
            name=name,
            index=faiss.read_index(str(index_path)),
            records=read_jsonl(metadata_path),
        )

    return TypedVectorStore(
        knowledge=namespaces["knowledge"],
        playbooks=namespaces["playbooks"],
    )



MAX_KNOWLEDGE_CHUNKS = 3

# Estes valores são uma configuração inicial conservadora. Eles precisam ser
# calibrados posteriormente com os cenários de avaliação do RAG.
SEMANTIC_TOPIC_MIN_SCORE = 0.30
SEMANTIC_TOPIC_MIN_MARGIN = 0.03

ALLOWED_STATUSES = {
    "machine_audited",
    "human_reviewed",
}


@dataclass(frozen=True)
class TopicCandidate:
    topic_id: str
    score: float


@dataclass(frozen=True)
class RetrievalResult:
    query_language: str
    topic_id: str | None
    topic_confidence: str
    topic_source: Literal["lexical", "semantic", "none"]
    topic_decision_reason: Literal[
        "lexical_match",
        "semantic_match",
        "ambiguous",
        "low_similarity",
        "no_candidates",
    ]
    topic_candidates: tuple[TopicCandidate, ...]
    playbook: RetrievedCandidate | None
    knowledge: tuple[RetrievedCandidate, ...]
    retrieval_warnings: tuple[str, ...]


@dataclass(frozen=True)
class SemanticTopicDecision:
    topic_id: str | None
    confidence: Literal["high", "low"]
    reason: Literal[
        "semantic_match",
        "ambiguous",
        "low_similarity",
        "no_candidates",
    ]
    score: float
    margin: float
    candidates: tuple[TopicCandidate, ...]


class TypedRetriever:
    def __init__(
        self,
        vector_store: TypedVectorStore,
        topic_classifier: LexicalTopicClassifier | None = None,
        embedder: OpenAIEmbedder | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.topic_classifier = topic_classifier or LexicalTopicClassifier()
        self.embedder = embedder or OpenAIEmbedder()

    @classmethod
    def from_build_artifacts(cls) -> TypedRetriever:
        return cls(vector_store=load_vector_store())

    def retrieve(
        self,
        normalized_english_query: str,
    ) -> RetrievalResult:
        # Quem chama este método deve traduzir/normalizar a mensagem original
        # e executar o Security Gate antes de iniciar a recuperação.
        lexical_classification = self.topic_classifier.classify(
            normalized_english_query
        )

        # O embedding é necessário para recuperar os chunks mesmo quando o
        # atalho lexical encontra um tópico. A mesma chamada é reaproveitada
        # pelo fallback semântico quando o atalho não encontra nada.
        query_vector = self.embedder.embed_query(
            normalized_english_query
        )

        # Pesquisamos todo o pequeno índice de knowledge uma única vez. Esses
        # candidatos servem tanto para inferir um tópico semanticamente quanto
        # para selecionar os chunks científicos no final.
        all_knowledge_candidates = (
            self.vector_store.knowledge.search_candidates(
                query_vector=query_vector,
                limit=self.vector_store.knowledge.size,
            )
        )

        if lexical_classification.topic_id is not None:
            topic_id = lexical_classification.topic_id
            topic_confidence = lexical_classification.confidence
            topic_source: Literal["lexical", "semantic", "none"] = "lexical"
            topic_decision_reason = "lexical_match"
            topic_candidates: tuple[TopicCandidate, ...] = ()
        else:
            semantic_decision = self._infer_semantic_topic(
                candidates=all_knowledge_candidates,
            )
            topic_id = semantic_decision.topic_id
            topic_confidence = semantic_decision.confidence
            topic_source = "semantic" if topic_id else "none"
            topic_decision_reason = semantic_decision.reason
            topic_candidates = semantic_decision.candidates

        if topic_id is None:
            # O fallback semântico também pode recusar a classificação quando
            # o melhor score é baixo ou muito próximo do segundo colocado.
            return RetrievalResult(
                query_language="en",
                topic_id=None,
                topic_confidence=topic_confidence,
                topic_source=topic_source,
                topic_decision_reason=topic_decision_reason,
                topic_candidates=topic_candidates,
                playbook=None,
                knowledge=(),
                retrieval_warnings=(
                    (
                        "Topic classification is ambiguous."
                        if topic_decision_reason == "ambiguous"
                        else "Topic confidence is insufficient for retrieval."
                    ),
                ),
            )

        # Recuperamos playbooks primeiro. Um playbook selecionado pode
        # priorizar os conceitos buscados na etapa de conhecimento.
        playbook_candidates = self._filter_candidates(
            candidates=self.vector_store.playbooks.search_candidates(
                query_vector=query_vector,
                limit=self.vector_store.playbooks.size,
            ),
            topic_id=topic_id,
            document_type="playbook",
        )

        playbook = self._select_playbook(
            candidates=playbook_candidates,
        )

        # A busca de conhecimento independe de existir playbook, mas um
        # playbook selecionado pode alterar o ranking final dos chunks.
        knowledge_candidates = self._filter_candidates(
            candidates=all_knowledge_candidates,
            topic_id=topic_id,
            document_type="knowledge",
        )

        knowledge = self._select_knowledge(
            candidates=knowledge_candidates,
            playbook=playbook,
        )

        warnings: list[str] = []

        if not playbook:
            warnings.append(
                "No playbook matched the selected topic."
            )

        if not knowledge:
            warnings.append(
                "No knowledge chunk matched the selected topic."
            )

        return RetrievalResult(
            query_language="en",
            topic_id=topic_id,
            topic_confidence=topic_confidence,
            topic_source=topic_source,
            topic_decision_reason=topic_decision_reason,
            topic_candidates=topic_candidates,
            playbook=playbook,
            knowledge=knowledge,
            retrieval_warnings=tuple(warnings),
        )

    @staticmethod
    def _infer_semantic_topic(
        candidates: list[RetrievedCandidate],
    ) -> SemanticTopicDecision:
        # Mantemos somente o melhor score de cada tópico. Isso evita favorecer
        # tópicos que possuem mais documentos no corpus.
        best_score_by_topic: dict[str, float] = {}

        for candidate in candidates:
            metadata = candidate.metadata

            if (
                metadata.get("document_type") != "knowledge"
                or metadata.get("language") != "en"
                or metadata.get("status") not in ALLOWED_STATUSES
            ):
                continue

            topic_id = metadata["topic_id"]
            current_score = best_score_by_topic.get(topic_id)

            if current_score is None or candidate.score > current_score:
                best_score_by_topic[topic_id] = candidate.score

        ranked_topics = sorted(
            best_score_by_topic.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        if not ranked_topics:
            return SemanticTopicDecision(
                topic_id=None,
                confidence="low",
                reason="no_candidates",
                score=0.0,
                margin=0.0,
                candidates=(),
            )

        best_topic_id, best_score = ranked_topics[0]
        second_score = ranked_topics[1][1] if len(ranked_topics) > 1 else 0.0
        margin = best_score - second_score
        topic_candidates = tuple(
            TopicCandidate(topic_id=topic_id, score=score)
            for topic_id, score in ranked_topics[:2]
        )

        if best_score < SEMANTIC_TOPIC_MIN_SCORE:
            return SemanticTopicDecision(
                topic_id=None,
                confidence="low",
                reason="low_similarity",
                score=best_score,
                margin=margin,
                candidates=topic_candidates,
            )

        if margin < SEMANTIC_TOPIC_MIN_MARGIN:
            return SemanticTopicDecision(
                topic_id=None,
                confidence="low",
                reason="ambiguous",
                score=best_score,
                margin=margin,
                candidates=topic_candidates,
            )

        return SemanticTopicDecision(
            topic_id=best_topic_id,
            confidence="high",
            reason="semantic_match",
            score=best_score,
            margin=margin,
            candidates=topic_candidates,
        )

    @staticmethod
    def _filter_candidates(
        candidates: list[RetrievedCandidate],
        topic_id: str,
        document_type: str,
    ) -> list[RetrievedCandidate]:
        # Apenas registros canônicos e seguros para produção podem seguir para
        # a seleção final da etapa atual de recuperação.
        return [
            candidate
            for candidate in candidates
            if candidate.metadata["topic_id"] == topic_id
            and candidate.metadata["document_type"] == document_type
            and candidate.metadata["language"] == "en"
            and candidate.metadata["status"] in ALLOWED_STATUSES
        ]

    @staticmethod
    def _select_playbook(
        candidates: list[RetrievedCandidate],
    ) -> RetrievedCandidate | None:
        # Os candidatos já foram encontrados semanticamente pelo FAISS e
        # filtrados pelo tópico. Aqui selecionamos o mais semelhante; as
        # trigger_phrases continuam disponíveis como metadados explicativos,
        # não como uma barreira rígida para a recuperação.
        return max(
            candidates,
            key=lambda candidate: candidate.score,
            default=None,
        )

    @staticmethod
    def _select_knowledge(
        candidates: list[RetrievedCandidate],
        playbook: RetrievedCandidate | None,
    ) -> tuple[RetrievedCandidate, ...]:
        preferred_concept_ids = set(
            playbook.metadata["related_concept_ids"]
            if playbook
            else []
        )

        # Conceitos relacionados ao playbook selecionado ficam antes dos
        # demais chunks do tópico. O score do FAISS desempata cada grupo.
        ranked_candidates = sorted(
            candidates,
            key=lambda candidate: (
                candidate.metadata["concept_id"]
                not in preferred_concept_ids,
                -candidate.score,
            ),
        )

        selected: list[RetrievedCandidate] = []
        selected_chunk_ids: set[str] = set()
        concept_counts: dict[str, int] = defaultdict(int)

        for candidate in ranked_candidates:
            concept_id = candidate.metadata["concept_id"]

            if candidate.chunk_id in selected_chunk_ids:
                continue

            if concept_counts[concept_id] >= 2:
                continue

            selected.append(candidate)
            selected_chunk_ids.add(candidate.chunk_id)
            concept_counts[concept_id] += 1

            if len(selected) == MAX_KNOWLEDGE_CHUNKS:
                break

        return tuple(selected)
