from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

import yaml

from Alfred.rag.paths import CORPUS_DIR


CANONICAL_DIR = CORPUS_DIR / "canonical"


@dataclass(frozen=True)
class TopicDefinition:
    topic_id: str
    title: str
    retrieval_terms: tuple[str, ...]
    concept_ids: tuple[str, ...]
    playbook_ids: tuple[str, ...]


@dataclass(frozen=True)
class TopicClassification:
    topic_id: str | None
    confidence: Literal["high", "low"]
    score: int
    matched_terms: tuple[str, ...]


def normalize_text(text: str) -> str:
    # Normaliza tanto a pergunta quanto os termos editoriais antes da busca
    # textual. Assim, maiúsculas, pontuação, hífens e espaços repetidos não
    # mudam o resultado da classificação.
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"[-_/]+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    # Os espaços extras evitam que um termo curto corresponda apenas a uma
    # parte de outra palavra.
    normalized_text = f" {normalize_text(text)} "
    normalized_phrase = f" {normalize_text(phrase)} "

    return normalized_phrase in normalized_text


def load_topics() -> tuple[TopicDefinition, ...]:
    # topic.yaml fornece vocabulário de roteamento e relações entre conceitos.
    # Ele nunca é usado como conteúdo científico na resposta ao usuário.
    topics: list[TopicDefinition] = []

    for path in sorted(CANONICAL_DIR.glob("*/topic.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError(f"Topic file '{path}' must contain a YAML object.")

        topics.append(
            TopicDefinition(
                topic_id=data["topic_id"],
                title=data["title"],
                retrieval_terms=tuple(data["retrieval_terms"]),
                concept_ids=tuple(data["concept_ids"]),
                playbook_ids=tuple(data["playbook_ids"]),
            )
        )

    if not topics:
        raise ValueError("No canonical topic files were found.")

    return tuple(topics)


class LexicalTopicClassifier:
    def __init__(
        self,
        topics: tuple[TopicDefinition, ...] | None = None,
    ) -> None:
        self.topics = topics or load_topics()

    def classify(self, query: str) -> TopicClassification:
        if not query.strip():
            raise ValueError("The retrieval query cannot be empty.")

        matches_by_topic: dict[str, tuple[str, ...]] = {}

        for topic in self.topics:
            # Um tópico pode aparecer pelo título, pelo ID ou por qualquer um
            # dos termos de recuperação revisados editorialmente.
            candidate_terms = (
                topic.title,
                topic.topic_id.replace("-", " "),
                *topic.retrieval_terms,
            )

            matched_terms = tuple(
                term
                for term in candidate_terms
                if contains_phrase(query, term)
            )

            matches_by_topic[topic.topic_id] = matched_terms

        scores = {
            topic_id: len(matched_terms)
            for topic_id, matched_terms in matches_by_topic.items()
        }

        highest_score = max(scores.values())
        highest_topics = tuple(
            topic_id
            for topic_id, score in scores.items()
            if score == highest_score
        )

        if highest_score == 0 or len(highest_topics) != 1:
            # Nenhuma correspondência ou um empate significa baixa confiança.
            # Não retornar tópico é mais seguro do que buscar contexto de um
            # assunto possivelmente incorreto.
            return TopicClassification(
                topic_id=None,
                confidence="low",
                score=highest_score,
                matched_terms=(),
            )

        topic_id = highest_topics[0]

        return TopicClassification(
            topic_id=topic_id,
            confidence="high",
            score=highest_score,
            matched_terms=matches_by_topic[topic_id],
        )
