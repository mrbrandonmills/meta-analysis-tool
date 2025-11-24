"""Main FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import meta_analysis, agents, studies, auth, health, reports, manuscripts, peer_reviews, researchers, reviewer_matcher, progress, researcher_enrichment, research_direction, subscriptions, payouts, review_approval, admin, tier_applications, admin_tier_applications
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.core.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    PerformanceMiddleware,
    ErrorHandlingMiddleware,
    rate_limiter,
)
from app.db.session import init_async_db, close_async_db

# Configure logging before initializing settings
configure_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Meta-Analysis Research Platform")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")

    # Validate Anthropic API key at startup
    if not settings.anthropic_api_key or settings.anthropic_api_key == "your_anthropic_api_key_here":
        error_msg = (
            "CRITICAL ERROR: Anthropic API key is missing or not configured. "
            "Please set ANTHROPIC_API_KEY environment variable. "
            "For Railway deployment, see RAILWAY_SETUP.md"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Validate API key format (should start with 'sk-ant-')
    if not settings.anthropic_api_key.startswith("sk-ant-"):
        error_msg = (
            "CRITICAL ERROR: Anthropic API key appears to be invalid (should start with 'sk-ant-'). "
            "Please check your ANTHROPIC_API_KEY environment variable."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("✓ Anthropic API key validated successfully")

    # CRITICAL FIX: Do NOT call init_async_db() in production
    # In production, Alembic migrations handle all database schema creation
    # Calling Base.metadata.create_all() conflicts with migration-created schemas
    # Only use init_async_db() for local development without migrations
    #
    # For production deployments:
    # 1. Run: alembic upgrade head
    # 2. Let FastAPI start without create_all()
    #
    # Initialize database (development only - migrations handle production)
    if settings.debug and "sqlite" in settings.database_url:
        # Only auto-create tables for local SQLite development
        try:
            await init_async_db()
            logger.info("✓ Database initialized successfully (development mode)")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # Continue anyway for development, but log the error
    else:
        logger.info("Skipping init_async_db() - using Alembic migrations for schema management")

    # Initialize rate limiter
    try:
        await rate_limiter.init()
        logger.info("✓ Rate limiter initialized successfully")
    except Exception as e:
        logger.warning(f"Rate limiter initialization failed: {e}")

    logger.info("✓ Meta-Analysis Research Platform started successfully")

    yield

    # Cleanup
    logger.info("Shutting down Meta-Analysis Research Platform")

    # Close database connections
    try:
        await close_async_db()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

    # Close rate limiter
    try:
        await rate_limiter.close()
        logger.info("✓ Rate limiter closed")
    except Exception as e:
        logger.error(f"Error closing rate limiter: {e}")

    logger.info("✓ Meta-Analysis Research Platform shut down successfully")


app = FastAPI(
    title="Meta-Analysis Research Platform",
    description="AI-powered meta-analysis using specialized research agents with authentication, background jobs, and production-ready infrastructure",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware (order matters - first added is outermost)
# 1. Error handling (catch all errors)
app.add_middleware(ErrorHandlingMiddleware)

# 2. Performance tracking
app.add_middleware(PerformanceMiddleware, slow_request_threshold=2.0)

# 3. Request ID tracking
app.add_middleware(RequestIDMiddleware)

# 4. Rate limiting (after request ID so we can log the request ID)
app.add_middleware(
    RateLimitMiddleware,
    authenticated_limit=100,  # 100 requests per minute for authenticated users
    unauthenticated_limit=20,  # 20 requests per minute for unauthenticated
    window_seconds=60,
)

# 5. CORS (last middleware, first to process)
allowed_origins = settings.allowed_origins.split(",") if settings.allowed_origins else ["*"]
# Always allow the Vercel frontend
allowed_origins.extend([
    "https://meta-analysis-tool.vercel.app",
    "https://meta-analysis-tool-brandons-projects-c4dfa14a.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
])
# Remove duplicates
allowed_origins = list(set(allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with platform information.

    Returns:
    - Platform name and version
    - Available tools
    - Documentation links
    """
    return {
        "name": "Meta-Analysis Research Platform",
        "version": "0.1.0",
        "status": "operational",
        "description": "AI-powered academic research platform with 4 tools",
        "tools": {
            "tool_1": "Meta-Analysis/Systematic Review Assistant (5/7 agents operational)",
            "tool_2": "Research Direction Generator (operational)",
            "tool_3": "Peer Review Quality Assistant (operational)",
            "tool_4": "Expert Reviewer Matcher (operational)",
        },
        "agents_available": 5,
        "agents_total": 25,
        "documentation": "/docs",
        "health_check": "/health",
    }


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(meta_analysis.router, prefix="/api/v1", tags=["meta-analysis"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(studies.router, prefix="/api/v1", tags=["studies"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(manuscripts.router, prefix="/api/v1", tags=["manuscripts"])
app.include_router(peer_reviews.router, prefix="/api/v1", tags=["peer-reviews"])
app.include_router(researchers.router, prefix="/api/v1", tags=["researchers"])
app.include_router(researcher_enrichment.router, prefix="/api/v1", tags=["researcher-enrichment"])
app.include_router(reviewer_matcher.router, prefix="/api/v1", tags=["reviewer-matcher"])
app.include_router(research_direction.router, prefix="/api/v1", tags=["research-direction"])
app.include_router(progress.router, prefix="/api/v1", tags=["progress"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
app.include_router(payouts.router, prefix="/api/v1/payouts", tags=["payouts"])
app.include_router(review_approval.router, prefix="/api/v1/review-approval", tags=["review-approval"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(tier_applications.router, prefix="/api/v1/tier-applications", tags=["tier-applications"])
app.include_router(admin_tier_applications.router, prefix="/api/v1/admin/tier-applications", tags=["admin-tier-applications"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
