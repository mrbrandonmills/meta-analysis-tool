"""Main FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import meta_analysis, agents, studies
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Meta-Analysis Research Platform")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")

    # Initialize databases, connections, etc.
    # TODO: Initialize database connection
    # TODO: Initialize vector database
    # TODO: Initialize agent registry

    yield

    # Cleanup
    logger.info("Shutting down Meta-Analysis Research Platform")


app = FastAPI(
    title="Meta-Analysis Research Platform",
    description="AI-powered meta-analysis using specialized research agents",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Meta-Analysis Research Platform",
        "version": "0.1.0",
        "status": "operational",
        "agents": "ready",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(meta_analysis.router, prefix="/api/v1", tags=["meta-analysis"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(studies.router, prefix="/api/v1", tags=["studies"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
