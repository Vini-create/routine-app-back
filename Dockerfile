FROM python:3.13-slim

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Required runtime data, copied explicitly so a missing audited corpus fails the
# image build instead of breaking only knowledge requests after deployment.
COPY Alfred/rag/corpus/build/chunks.jsonl Alfred/rag/corpus/build/manifest.json /app/Alfred/rag/corpus/build/
COPY Alfred/rag/corpus/build/faiss/ /app/Alfred/rag/corpus/build/faiss/

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
