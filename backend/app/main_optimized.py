from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import init_db
from app.core.middleware import (
    RateLimitMiddleware,
    RequestTimingMiddleware,
    ErrorHandlingMiddleware,
    CORSCustomMiddleware
)
from app.api.api_v1 import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")

    # Create upload directory if it doesn't exist
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory ready: {settings.UPLOAD_DIR}")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app with optimized configuration
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered chatbot SaaS platform with RAG capabilities",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
    # Optimize response model generation
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
)

# Security middleware - add first (applied last)
app.add_middleware(CORSCustomMiddleware)

# Error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# Request timing middleware
app.add_middleware(RequestTimingMiddleware)

# Rate limiting middleware (customize as needed)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.RATE_LIMIT_PER_MINUTE,
        period=60
    )

# Trusted host middleware (production only)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.azolute.com", "azolute.com"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Azolute AI Chatbot API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    try:
        # Check database connection
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    # In production, integrate with Prometheus or similar
    return {
        "status": "ok",
        "message": "Metrics endpoint - integrate with monitoring system"
    }


# Exception handlers
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error occurred",
            "message": "Please try again later"
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main_optimized:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        workers=4 if settings.ENVIRONMENT == "production" else 1,
        log_level="info",
    )
