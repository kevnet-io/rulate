# Production Ready

> Deploy Rulate to production with confidence

## Status

- **Phase**: Complete ✅
- **Completed**: December 2025
- **Follow-up**: See Epic 10 (Production Hardening) for security integration and enhancements

## Context

Rulate's core engine is complete and well-tested, but deploying to production requires additional infrastructure: containerization, health monitoring, proper configuration management, and security hardening. This epic addresses the gap between "works on my machine" and "production-ready service."

## Success Criteria

- [x] Single `docker-compose up` command starts the full stack
- [x] Health endpoint reports service status and dependencies
- [x] Configuration managed via environment variables
- [x] Comprehensive deployment documentation (Docker-focused)
- [x] Security utilities created (integration pending - see Epic 10)

## Deliverables

### Docker Configuration

**Current State**: No containerization. Manual setup required.

**Goal**: One-command deployment with Docker.

#### Production Deployment Options

**Option A: Single Container (Simple)**
- One Dockerfile for unified server
- Builds frontend during image build
- FastAPI serves both API and frontend
- Best for: Small deployments, quick setup

**Option B: Multi-Container (Scalable)**
- Separate API and frontend containers
- Independent scaling
- CDN for frontend assets
- Best for: Production scale, high traffic

**Tasks**:
- [ ] Create `Dockerfile` for unified server (Option A)
- [ ] Create separate `Dockerfile` for API server (Option B, multi-stage build)
- [ ] Create separate `Dockerfile` for Web UI (Option B, nginx serving built assets)
- [ ] Create `docker-compose.yml` for full stack (API + Web + SQLite volume)
- [ ] Create `docker-compose.dev.yml` for development with hot reload
- [ ] Add health checks to container definitions
- [ ] Document environment variables

Current roadmap focuses on Option A first for simplicity, with Option B for future scalability needs.

### Health Check Endpoint

**Current State**: No health check endpoint.

**Goal**: Kubernetes/container-orchestrator friendly health reporting.

**Tasks**:
- [ ] Add `GET /health` endpoint returning status, version, and dependency health
- [ ] Check database connectivity in health response
- [ ] Add readiness probe (for Kubernetes)
- [ ] Add liveness probe (for Kubernetes)

**Example response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "uptime_seconds": 3600
}
```

### Advanced Logging

**Current State**: Basic print/logging statements.

**Goal**: Production-grade structured logging.

**Tasks**:
- [ ] Implement structured logging with JSON format (using `structlog`)
- [ ] Configure log levels per module
- [ ] Add request/response logging middleware
- [ ] Document error tracking integration (Sentry, etc.)

### Environment Configuration

**Current State**: Hardcoded configuration values.

**Goal**: Flexible, secure configuration management.

**Tasks**:
- [ ] Add `.env` file support with `pydantic-settings`
- [ ] Create environment-specific configurations (dev, staging, prod)
- [ ] Document all configuration options
- [ ] Add CORS configuration via environment variables

### Deployment Guide

**Current State**: Basic "run uvicorn" and "npm run dev" in README.

**Goal**: Step-by-step deployment for common platforms.

**Tasks**:
- [ ] Write deployment guide for Docker-based deployment
- [ ] Add cloud deployment examples (AWS ECS, GCP Cloud Run, DigitalOcean App Platform)
- [ ] Create Kubernetes manifests (Deployment, Service, Ingress)
- [ ] Document production checklist (security, monitoring, backups)

### HTTPS/TLS

**Current State**: Development uses HTTP only.

**Goal**: Secure communication in production.

**Tasks**:
- [ ] Document SSL/TLS configuration with reverse proxy (nginx, Traefik)
- [ ] Add certificate management guidance (Let's Encrypt, cert-manager)
- [ ] Configure HTTP to HTTPS redirect

### Input Sanitization Audit

**Current State**: Basic Pydantic validation.

**Goal**: Defense against common attack vectors.

**Tasks**:
- [ ] Audit all input validation for edge cases
- [ ] Add XSS prevention measures in Web UI
- [ ] Implement YAML/JSON bomb prevention (max depth, max size)
- [ ] Add file size limits for imports
- [ ] Document security considerations

## Dependencies

None - this epic is foundational.

## Open Questions

- Should we support multiple database backends (SQLite, PostgreSQL) from the start, or add PostgreSQL later?
- What container registry should be used for published images?
