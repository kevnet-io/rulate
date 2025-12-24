"""
FastAPI application for Rulate.

This provides a REST API for managing schemas, rulesets, catalogs, and items,
as well as evaluating compatibility between items.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.database.connection import init_db
from api.logging_config import configure_logging, get_logger
from api.middleware.logging import LoggingMiddleware
from api.routers import (
    catalogs,
    clusters,
    evaluation,
    health,
    import_export,
    rulesets,
    schemas,
)


# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    configure_logging()
    logger = get_logger(__name__)
    logger.info("application_startup", environment=settings.environment)

    init_db()
    logger.info("database_initialized")

    yield

    # Shutdown
    logger.info("application_shutdown")


# Create FastAPI app
app = FastAPI(
    title="Rulate API",
    description="Rule-based comparison engine for evaluating relationships between objects",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS - only in development mode
if settings.is_development and settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# Production: no CORS needed (same-origin)

# Add request/response logging middleware
if not settings.is_development:  # Only in staging/production
    app.add_middleware(LoggingMiddleware)

# Mount static files for frontend (if built)
FRONTEND_BUILD_DIR = settings.frontend_build_dir

if FRONTEND_BUILD_DIR.exists():
    # Mount _app directory for SvelteKit assets (JS, CSS, etc.)
    app.mount(
        "/_app",
        StaticFiles(directory=str(FRONTEND_BUILD_DIR / "_app")),
        name="frontend-assets",
    )

# Include routers
# Health check router (no prefix - top-level routes)
app.include_router(health.router, tags=["health"])

# API routers
app.include_router(schemas.router, prefix="/api/v1", tags=["schemas"])
app.include_router(rulesets.router, prefix="/api/v1", tags=["rulesets"])
app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["evaluation"])
app.include_router(clusters.router, prefix="/api/v1", tags=["clusters"])
app.include_router(import_export.router, prefix="/api/v1", tags=["import-export"])


@app.get("/")
async def root():
    """Serve frontend homepage."""
    index_path = FRONTEND_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "Frontend not built. Run: cd web && npm run build",
        "api_docs": "/docs",
        "api_version": "0.1.0",
    }


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve SvelteKit SPA for all routes not handled by API."""
    # Don't intercept API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)

    # Validate frontend exists
    if not FRONTEND_BUILD_DIR.exists():
        raise HTTPException(
            status_code=503, detail="Frontend not built. Run: cd web && npm run build"
        )

    # Security: Validate path stays within build directory to prevent traversal attacks
    # Resolves symlinks and normalizes paths (e.g., '../../../etc/passwd')
    build_root = FRONTEND_BUILD_DIR.resolve()
    requested_path = (build_root / full_path.lstrip("/")).resolve(strict=False)

    try:
        requested_path.relative_to(build_root)
    except ValueError:
        raise HTTPException(status_code=404)

    # Serve static files if they exist
    if requested_path.is_file():
        return FileResponse(requested_path)

    # Otherwise serve index.html (SPA routing)
    index_path = build_root / "index.html"
    return FileResponse(index_path)
