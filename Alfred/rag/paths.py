from pathlib import Path


# Todos os caminhos do RAG partem deste pacote. Isso evita espalhar pelo
# projeto suposicoes sobre uma antiga pasta ``rag`` na raiz do repositorio.
RAG_PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RAG_PACKAGE_DIR.parents[1]

CORPUS_DIR = RAG_PACKAGE_DIR / "corpus"
BUILD_DIR = CORPUS_DIR / "build"
INDEX_DIR = BUILD_DIR / "faiss"
DOCS_DIR = RAG_PACKAGE_DIR / "docs"
