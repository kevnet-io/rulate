"""
FastAPI application for Rulate.

This provides a REST API for managing schemas, rulesets, catalogs, and items,
as well as evaluating compatibility between items.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database.connection import init_db
from api.routers import catalogs, clusters, evaluation, import_export, rulesets, schemas


# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


# Create FastAPI app
app = FastAPI(
    title="Rulate API",
    description="Rule-based comparison engine for evaluating relationships between objects",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(schemas.router, prefix="/api/v1", tags=["schemas"])
app.include_router(rulesets.router, prefix="/api/v1", tags=["rulesets"])
app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["evaluation"])
app.include_router(clusters.router, prefix="/api/v1", tags=["clusters"])
app.include_router(import_export.router, prefix="/api/v1", tags=["import-export"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Rulate API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
