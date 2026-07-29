"""Production composition for Alfred's precomputed hybrid retriever."""

import json
from functools import lru_cache
from pathlib import Path

import faiss
import numpy as np

from app.ai.retrieval.corpus import MANIFEST_PATH as CORPUS_MANIFEST_PATH
from app.ai.retrieval.corpus import load_production_corpus
from app.ai.retrieval.embeddings import build_query_embeddings
from app.ai.retrieval.hybrid import HybridKnowledgeRetriever
from app.core.config import settings

FAISS_BUILD_DIR = (
    Path(__file__).resolve().parents[3]
    / "Alfred"
    / "rag"
    / "corpus"
    / "build"
    / "faiss"
)
FAISS_MANIFEST_PATH = FAISS_BUILD_DIR / "manifest.json"


def _load_precomputed_vectors(
    chunk_ids: tuple[str, ...],
) -> np.ndarray:
    manifest = json.loads(FAISS_MANIFEST_PATH.read_text(encoding="utf-8"))
    corpus_manifest = json.loads(
        CORPUS_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    if manifest.get("chunks_sha256") != corpus_manifest.get("chunks_sha256"):
        raise ValueError("The FAISS index was built from a different corpus.")
    if manifest.get("embedding_model") != settings.ai_embedding_model:
        raise ValueError(
            "The configured embedding model does not match the FAISS index."
        )

    vectors_by_chunk: dict[str, np.ndarray] = {}
    expected_dimension: int | None = None
    for namespace in manifest.get("indexes", {}).values():
        index_path = FAISS_BUILD_DIR / namespace["index_file"]
        metadata_path = FAISS_BUILD_DIR / namespace["metadata_file"]
        index = faiss.read_index(str(index_path))
        records = [
            json.loads(line)
            for line in metadata_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if index.ntotal != len(records):
            raise ValueError("The FAISS index and metadata cardinalities differ.")
        if index.d != namespace["dimension"]:
            raise ValueError("The FAISS index dimension differs from its manifest.")
        if expected_dimension is None:
            expected_dimension = index.d
        elif index.d != expected_dimension:
            raise ValueError("The FAISS namespaces use different dimensions.")
        for position, record in enumerate(records):
            chunk_id = record.get("chunk_id")
            if not isinstance(chunk_id, str) or chunk_id in vectors_by_chunk:
                raise ValueError("The FAISS metadata contains an invalid chunk ID.")
            vectors_by_chunk[chunk_id] = np.asarray(
                index.reconstruct(position),
                dtype=np.float32,
            )

    if set(vectors_by_chunk) != set(chunk_ids):
        raise ValueError("The FAISS vectors do not match the approved corpus.")
    return np.stack([vectors_by_chunk[chunk_id] for chunk_id in chunk_ids])


@lru_cache(maxsize=1)
def build_default_knowledge_retriever() -> HybridKnowledgeRetriever:
    """Load audited document vectors; only user queries require embedding."""

    documents = load_production_corpus()
    return HybridKnowledgeRetriever(
        documents=documents,
        embeddings=build_query_embeddings(),
        document_vectors=_load_precomputed_vectors(
            tuple(document.chunk_id for document in documents)
        ),
    )
