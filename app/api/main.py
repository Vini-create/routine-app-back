from uuid import UUID, uuid4
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth_routes import auth_router, users_router
from app.api.routine_routes import routine_router
from app.api.ai_routes import ai_router
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.core.config import settings
from app import models as registered_models
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler
from app.api.rate_limit import limiter

app = FastAPI()
_ = registered_models  # Register SQLAlchemy models before create_all/autogenerate.

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    cast(Any, _rate_limit_exceeded_handler),
)


_AI_ERROR_STATUS = {
    AIErrorCode.IDEMPOTENCY_KEY_REUSED: 409,
    AIErrorCode.CONVERSATION_NOT_FOUND: 404,
    AIErrorCode.PATCH_NOT_FOUND: 404,
    AIErrorCode.CONVERSATION_FORBIDDEN: 403,
    AIErrorCode.USER_CONTEXT_FORBIDDEN: 403,
    AIErrorCode.PATCH_FORBIDDEN: 403,
    AIErrorCode.PLAN_UNAVAILABLE: 403,
    AIErrorCode.PATCH_EXPIRED: 410,
    AIErrorCode.PATCH_ALREADY_RESOLVED: 409,
    AIErrorCode.RATE_LIMIT_EXCEEDED: 429,
    AIErrorCode.DAILY_QUOTA_EXCEEDED: 429,
    AIErrorCode.DAILY_STANDARD_LIMIT_EXCEEDED: 429,
    AIErrorCode.DAILY_RAG_LIMIT_EXCEEDED: 429,
    AIErrorCode.WEEKLY_DEEP_ANALYSIS_LIMIT_EXCEEDED: 429,
    AIErrorCode.CONCURRENT_STREAM_LIMIT_EXCEEDED: 429,
    AIErrorCode.GLOBAL_COST_LIMIT_EXCEEDED: 503,
    AIErrorCode.MODEL_UNAVAILABLE: 503,
    AIErrorCode.GRAPH_EXECUTION_FAILED: 503,
}


@app.exception_handler(AIApplicationError)
async def ai_application_error_handler(
    request: Request,
    error: AIApplicationError,
) -> JSONResponse:
    del request
    try:
        request_id = UUID(error.request_id) if error.request_id else uuid4()
    except ValueError:
        request_id = uuid4()
    return JSONResponse(
        status_code=_AI_ERROR_STATUS.get(error.code, 400),
        content={
            "request_id": str(request_id),
            "code": error.code.value,
            "message": error.message,
            "details": {},
        },
    )
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(routine_router)
app.include_router(ai_router)
