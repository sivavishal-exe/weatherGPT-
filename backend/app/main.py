import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.logging import logger
from app.core.database import init_db
from app.core.redis_cache import cache
from app.core.security import rate_limiter
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for async startup and shutdown tasks."""
    logger.info("Initializing WeatherGPT Backend Infrastructure...")
    await init_db()
    await cache.connect()
    yield
    logger.info("Shutting down WeatherGPT Backend Infrastructure...")
    await cache.close()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Grounded AI Conversational Weather Intelligence API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Security Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Global Structured Error Handlers (Hides stack traces from clients)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException [{exc.status_code}]: {exc.detail} path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": exc.status_code,
                "type": "HTTPException",
                "message": exc.detail
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"ValidationError path={request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,

        content={
            "status": "error",
            "error": {
                "code": 422,
                "type": "ValidationError",
                "message": "Invalid request parameters or payload structure."
            }
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log internal error details privately
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    # Return safe, non-leaking error response to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": {
                "code": 500,
                "type": "InternalServerError",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    """
    Applies security headers, rate-limiting, and request timing.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    start_time = time.time()

    if rate_limiter.is_rate_limited(client_ip, start_time):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "status": "error",
                "error": {
                    "code": 429,
                    "type": "RateLimitExceeded",
                    "message": "Too many requests. Rate limit exceeded."
                }
            }
        )

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


# Include API Routers under /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health_check():
    """Health check endpoint for status monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
