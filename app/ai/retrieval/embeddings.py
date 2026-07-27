"""LangChain-backed local multilingual embeddings."""

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings


class E5MultilingualEmbeddings(Embeddings):
    """Apply the asymmetric prefixes required by multilingual E5."""

    def __init__(self, client: Embeddings) -> None:
        self._client = client

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            raise ValueError("At least one document is required for embedding.")
        return self._client.embed_documents(
            [f"passage: {text.strip()}" for text in texts]
        )

    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("The retrieval query cannot be empty.")
        return self._client.embed_query(f"query: {text.strip()}")


@lru_cache(maxsize=1)
def build_local_multilingual_embeddings() -> Embeddings:
    """Build one process-wide local model; no API key or paid call is used."""

    client = HuggingFaceEmbeddings(
        model_name=settings.ai_embedding_model,
        model_kwargs={"device": settings.ai_embedding_device},
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": settings.ai_embedding_batch_size,
        },
    )
    return E5MultilingualEmbeddings(client)
