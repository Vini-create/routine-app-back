from fastapi import FastAPI
from app.api.auth_routes import auth_router
import app.models #force the models to be registered before the app starts, ensuring that all tables are created when using SQLAlchemy's create_all() method.
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler
from app.api.rate_limit import limiter

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)