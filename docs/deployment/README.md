# Rulate Deployment Guide

Quick guide for deploying Rulate to production.

## Quick Start with Docker

The fastest way to deploy Rulate is using Docker Compose:

```bash
# 1. Clone and configure
git clone <repo-url>
cd rulate
cp .env.production.example .env

# 2. Start with Docker Compose
docker-compose up -d

# 3. Access application
open http://localhost:8000
```

## Docker Commands

```bash
# Build image
make docker-build

# Start production server (detached)
make docker-up

# View logs
make docker-logs

# Stop containers
make docker-down

# Clean up
make docker-clean
```

## Environment Configuration

Rulate uses environment variables for configuration. Key settings:

```bash
# Application
ENVIRONMENT=production  # development, staging, or production
LOG_LEVEL=INFO         # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json        # json or text

# Database
DATABASE_URL=sqlite:////app/data/rulate.db

# Security
MAX_UPLOAD_SIZE_MB=10
YAML_MAX_DEPTH=20
YAML_MAX_ALIASES=100
```

See `.env.production.example` for all available options.

## Health Check Endpoints

Rulate provides Kubernetes-ready health check endpoints:

- `GET /health` - Comprehensive health status with database check
- `GET /health/ready` - Readiness probe (ready to receive traffic)
- `GET /health/live` - Liveness probe (application is alive)

Example:
```bash
curl http://localhost:8000/health
```

## Production Checklist

Before deploying to production:

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure `DATABASE_URL` (consider PostgreSQL for scale)
- [ ] Set `LOG_FORMAT=json` for log aggregation
- [ ] Configure appropriate `CORS_ORIGINS` if using separate frontend
- [ ] Review file upload limits (`MAX_UPLOAD_SIZE_MB`)
- [ ] Set up HTTPS with reverse proxy (nginx, Traefik, Caddy)
- [ ] Configure database backups
- [ ] Set up monitoring and alerting

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTPS
┌──────▼──────────┐
│ Reverse Proxy   │  (Nginx/Traefik/Caddy)
│ - SSL/TLS       │
└──────┬──────────┘
       │ HTTP
┌──────▼──────────┐
│ Rulate Container│
│ - FastAPI       │
│ - SvelteKit UI  │
│ - SQLite DB     │
└─────────────────┘
```

## Monitoring

Rulate provides structured JSON logging in production:

```json
{
  "event": "http_request_completed",
  "level": "info",
  "timestamp": "2025-12-24T10:30:00Z",
  "app": "Rulate API",
  "version": "0.1.0",
  "environment": "production",
  "method": "GET",
  "path": "/api/v1/schemas",
  "status_code": 200,
  "duration_ms": 45.2
}
```

Integrate with log aggregation tools (ELK, CloudWatch, Datadog) for monitoring.

## Support

For detailed deployment guides:
- See comprehensive plan in `.claude/plans/production-ready.md`
- Check CLAUDE.md for development commands
- Review README.md for project overview

For issues:
- GitHub Issues: <repo-url>/issues
