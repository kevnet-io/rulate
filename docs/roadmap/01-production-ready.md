# Production Ready

> Deploy Rulate to production with confidence

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

Rulate's core engine is complete and well-tested, but deploying to production requires additional infrastructure: containerization, health monitoring, proper configuration management, and security hardening. This epic addresses the gap between "works on my machine" and "production-ready service."

## Success Criteria

- [ ] Single `docker-compose up` command starts the full stack
- [ ] Health endpoint reports service status and dependencies
- [ ] Configuration managed via environment variables
- [ ] Comprehensive deployment documentation for major cloud providers
- [ ] Security audit completed with no critical issues

## Deliverables

### Docker Configuration

**Current State**: No containerization. Manual setup required.

**Goal**: One-command deployment with Docker.

**Tasks**:
- [ ] Create `Dockerfile` for API server (multi-stage build for size optimization)
- [ ] Create `Dockerfile` for Web UI (nginx serving built assets)
- [ ] Create `docker-compose.yml` for full stack (API + Web + SQLite volume)
- [ ] Create `docker-compose.dev.yml` for development with hot reload
- [ ] Add health checks to container definitions
- [ ] Document environment variables

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
