"""Production composition for the local knowledge retriever."""

from functools import lru_cache

from app.ai.retrieval.corpus import load_production_corpus
from app.ai.retrieval.embeddings import build_local_multilingual_embeddings
from app.ai.retrieval.hybrid import HybridKnowledgeRetriever


@lru_cache(maxsize=1)
def build_default_knowledge_retriever() -> HybridKnowledgeRetriever:
    """Load the approved corpus and embed it once per application process."""

    return HybridKnowledgeRetriever(
        documents=load_production_corpus(),
        embeddings=build_local_multilingual_embeddings(),
    )
