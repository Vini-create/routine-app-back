"""LangChain-backed query embeddings for the precomputed Alfred index."""

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


@lru_cache(maxsize=1)
def build_query_embeddings() -> Embeddings:
    """Build a lightweight client matching the committed FAISS vectors."""

    return OpenAIEmbeddings(
        model=settings.ai_embedding_model,
        api_key=settings.openai_api_key,
        max_retries=settings.ai_model_max_retries,
        timeout=settings.ai_model_timeout_seconds,
    )
