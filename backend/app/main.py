from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.endpoints.auth import limiter
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.database.connection import close_mongo_connection, connect_to_mongo
from app.database.indexes import create_indexes
from app.database.seed import seed_categories
from fastapi.exceptions import HTTPException, RequestValidationError


@asynccontextmanager
async def lifespan(_app: FastAPI):
    import os

    if os.getenv("TESTING") == "true":
        yield
        return
    await connect_to_mongo()
    await create_indexes()
    from app.database.connection import get_database

    await seed_categories(get_database())
    yield
    await close_mongo_connection()


def create_app() -> FastAPI:
    import os

    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    app.state.limiter = limiter
    if os.getenv("TESTING") == "true":
        limiter.enabled = False
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health")
    async def health():
        return {"success": True, "message": "OK", "data": {"status": "healthy"}}

    return app


app = create_app()
