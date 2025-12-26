# Multi-stage build for Rulate production deployment
# Stage 1: Build frontend
FROM node:22-slim AS frontend-builder

WORKDIR /app/web

# Copy frontend package files
COPY web/package*.json ./

# Install dependencies
RUN corepack install && corepack enable npm && npm ci

# Copy frontend source
COPY web/ ./

# Build frontend
RUN npm run build

# Stage 2: `uv` binary
FROM ghcr.io/astral-sh/uv:0.9.18 AS uv

# Stage 3: Python application
FROM python:3.14-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv from its official container image to a location in the PATH
COPY --from=uv /uv /usr/local/bin/

# Copy Python dependencies (+ README for `uv sync`)
COPY pyproject.toml uv.lock README.md ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY rulate/ ./rulate/
COPY api/ ./api/

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/web/build ./web/build/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
