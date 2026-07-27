FROM python:3.13-slim

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV HF_HOME=/opt/huggingface
ENV HF_HUB_DISABLE_TELEMETRY=1

ARG AI_EMBEDDING_MODEL=intfloat/multilingual-e5-small
ENV AI_EMBEDDING_MODEL=${AI_EMBEDDING_MODEL}

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Bake the local multilingual embedding model into the Railway image. Runtime
# RAG requests therefore need neither a Hugging Face token nor a cold download.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${AI_EMBEDDING_MODEL}')"

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
