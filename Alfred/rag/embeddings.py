from __future__ import annotations

import math
import os
from dataclasses import dataclass

from langchain_openai import OpenAIEmbeddings

from Alfred.rag.chunks import EMBEDDING_MODEL


@dataclass(frozen=True)
class EmbeddingConfig:
    model: str = EMBEDDING_MODEL
    batch_size: int = 64


class OpenAIEmbedder:
    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        self.config = config or EmbeddingConfig()

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is required to generate embeddings."
            )

        self._client = OpenAIEmbeddings(
            model=self.config.model,
            chunk_size=self.config.batch_size,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            raise ValueError("At least one text is required to create embeddings.")

        vectors = self._client.embed_documents(texts)
        return self._validate_vectors(vectors, expected_count=len(texts))

    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("The query text cannot be empty.")

        vector = self._client.embed_query(text)
        return self._validate_vectors([vector], expected_count=1)[0]

    @staticmethod
    def _validate_vectors(
        vectors: list[list[float]],
        expected_count: int,
    ) -> list[list[float]]:
        if len(vectors) != expected_count:
            raise RuntimeError(
                f"Expected {expected_count} embeddings, received {len(vectors)}."
            )

        dimensions = {len(vector) for vector in vectors}

        if len(dimensions) != 1 or 0 in dimensions:
            raise RuntimeError(
                "All embeddings must have the same non-zero dimension."
            )

        if any(not math.isfinite(value) for vector in vectors for value in vector):
            raise RuntimeError("Embeddings must contain only finite numeric values.")

        return vectors
