# Production Hardening & Security Integration

> Harden production infrastructure and complete security integration

## Status

- **Phase**: Planning
- **Last Updated**: December 2024
- **Priority**: High (follows Production Ready epic completion)

## Context

The Production Ready epic (Epic 01) delivered excellent infrastructure foundations: configuration management, structured logging, health checks, Docker containerization, and security utilities. However, code review identified critical integration gaps and missing production features that should be addressed before exposing the API to real traffic.

**Key Finding**: Security utilities were created but not integrated into endpoints, creating a "security system installed but not turned on" scenario.

## Success Criteria

- [x] Security functions integrated into all relevant endpoints
- [ ] API rate limiting prevents abuse and DoS attacks
- [ ] Secrets management supports future authentication features
- [ ] PostgreSQL support enables production database scalability
- [ ] Database migrations enable schema evolution without downtime
- [ ] Observability metrics expose application performance data
- [ ] Security audit shows all critical gaps addressed

## Deliverables

### Phase 1: Security Integration (Critical - Week 1)

**Problem**: `validate_file_upload()` and `sanitize_catalog_name()` exist in `api/security.py` but are unused.

**Impact**: High - No actual protection despite having security code

**Tasks**:
- [ ] Integrate `validate_file_upload()` into import/export endpoints
  - `api/routers/import_export.py` - All import endpoints (4 endpoints)
  - Add file size validation before processing
  - Add comprehensive error messages for oversized files
- [ ] Integrate `sanitize_catalog_name()` into catalog operations
  - `api/routers/catalogs.py` - Create, get, update, delete endpoints
  - `api/routers/items.py` - All item operations that accept catalog names in path
  - Prevent path traversal attacks
- [ ] Add integration tests for security validations
  - Test oversized file rejection in import endpoints
  - Test path traversal rejection in catalog operations
  - Verify proper error responses (400 vs 413 vs 422)
- [ ] Fix misleading comment in `rulate/utils/loaders.py:85`
  - Current: "Use SafeYAMLLoader with depth and alias limits"
  - Correct: "Use SafeYAMLLoader with depth limits to prevent YAML bombs"

**Estimated Effort**: 2-3 hours

### Phase 2: Rate Limiting (Critical - Week 1)

**Problem**: No rate limiting on any endpoints - vulnerable to abuse and DoS

**Impact**: High - API can be overwhelmed by malicious or buggy clients

**Tasks**:
- [ ] Add `slowapi` dependency to `pyproject.toml`
- [ ] Configure global rate limiter with remote address tracking
- [ ] Apply limits to evaluation endpoints (highest compute cost)
  - `/api/v1/evaluate/matrix` - 10 requests/minute
  - `/api/v1/evaluate/clusters` - 5 requests/minute
  - `/api/v1/evaluate/pair` - 20 requests/minute
- [ ] Apply limits to import endpoints (highest I/O cost)
  - All `/api/v1/import/*` endpoints - 5 requests/minute
- [ ] Configure rate limit storage (in-memory for single instance, Redis for multi-instance)
- [ ] Add rate limit headers to responses (X-RateLimit-Limit, X-RateLimit-Remaining)
- [ ] Add rate limit exceeded handler with clear error messages
- [ ] Add `RATE_LIMIT_ENABLED` config flag (default: true in production)
- [ ] Add integration tests for rate limiting behavior

**Estimated Effort**: 4-6 hours

### Phase 3: Secrets Management (High Priority - Week 2)

**Problem**: No secret key management for future authentication/sessions

**Impact**: Medium - Blocks future auth features, forces hardcoded secrets

**Tasks**:
- [ ] Add `SECRET_KEY` to `api/config.py`
  - Generate secure default with `secrets.token_urlsafe(32)`
  - Require override in production via env var
  - Add validation: minimum length 32 characters
- [ ] Add secrets validation on startup
  - Warn if using default secret in production
  - Fail if SECRET_KEY is empty or too short
- [ ] Document secret generation in deployment guide
  - Add example: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - Add to production checklist
- [ ] Add support for secrets from files (Docker secrets, Kubernetes secrets)
  - `SECRET_KEY_FILE` env var for reading from file
  - Useful for orchestration platforms

**Estimated Effort**: 2-3 hours

### Phase 4: PostgreSQL Support (High Priority - Week 2-3)

**Problem**: SQLite only - not suitable for production scale or concurrent writes

**Impact**: Medium - Limits deployment options and scalability

**Tasks**:
- [ ] Add PostgreSQL driver to dependencies
  - `psycopg2-binary>=2.9.0` for PostgreSQL
  - `pymysql>=1.1.0` for MySQL (optional)
- [ ] Add connection pooling configuration
  - `POOL_SIZE` (default: 5)
  - `MAX_OVERFLOW` (default: 10)
  - `POOL_TIMEOUT` (default: 30)
  - `POOL_RECYCLE` (default: 3600)
- [ ] Update `api/database/connection.py` to support multiple databases
  - Auto-detect database type from URL
  - Apply appropriate engine parameters
- [ ] Add PostgreSQL to docker-compose.yml as optional service
  - Include example connection string
  - Include volume for data persistence
- [ ] Update deployment documentation
  - Add PostgreSQL setup instructions
  - Add connection string examples
  - Add performance tuning recommendations
- [ ] Add integration tests with PostgreSQL (optional, CI matrix)

**Estimated Effort**: 6-8 hours

### Phase 5: Database Migrations (High Priority - Week 3)

**Problem**: No migration system - schema changes require manual SQL or data loss

**Impact**: Medium - Risky deployments, no rollback capability

**Tasks**:
- [ ] Add Alembic dependency (`alembic>=1.12.0`)
- [ ] Initialize Alembic configuration
  - `alembic init alembic`
  - Configure `alembic.ini` to use application settings
  - Update `env.py` to use SQLAlchemy models
- [ ] Create initial migration from current schema
  - Generate baseline migration
  - Test against empty database
- [ ] Add migration commands to Makefile
  - `make migrate` - Run pending migrations
  - `make migration` - Generate new migration
  - `make migration-history` - Show migration history
  - `make migration-rollback` - Rollback last migration
- [ ] Update Dockerfile to run migrations on startup
  - Add migration check before starting server
  - Fail fast if migrations are pending
- [ ] Document migration workflow
  - How to create migrations
  - How to test migrations
  - Rollback procedures

**Estimated Effort**: 6-8 hours

### Phase 6: Request Validation & Limits (Medium Priority - Week 4)

**Problem**: No limits on request body size, query parameters, or batch operations

**Impact**: Medium - Resource exhaustion possible

**Tasks**:
- [ ] Add max request body size to config
  - `MAX_REQUEST_SIZE_MB` (default: 10MB)
  - Apply globally via middleware
- [ ] Add max query parameter limits
  - `MAX_QUERY_PARAMS` (default: 100)
  - `MAX_QUERY_STRING_LENGTH` (default: 4096)
- [ ] Add batch operation limits
  - Import: max 1000 items per request
  - Export: max 10000 items per response (with pagination)
- [ ] Add TrustedHost middleware for production
  - Configure allowed hosts from env var
  - Prevent host header injection
- [ ] Add request timeout configuration
  - `REQUEST_TIMEOUT` (default: 60 seconds)
- [ ] Add comprehensive tests for all limits

**Estimated Effort**: 4-6 hours

### Phase 7: Observability & Metrics (Medium Priority - Week 4-5)

**Problem**: No metrics, no tracing, no error tracking beyond logs

**Impact**: Low-Medium - Blind to performance issues and errors

**Tasks**:
- [ ] Add Prometheus metrics
  - Install `prometheus-fastapi-instrumentator`
  - Expose `/metrics` endpoint
  - Track request count, latency, errors
  - Track evaluation performance (duration, result distribution)
- [ ] Add error tracking (optional)
  - Sentry integration for error reporting
  - `SENTRY_DSN` environment variable
  - Attach request context to errors
- [ ] Add OpenTelemetry tracing (optional)
  - Distributed tracing for request flows
  - Trace evaluation operations
  - Export to Jaeger or Zipkin
- [ ] Update deployment docs with observability setup
  - Prometheus scraping configuration
  - Grafana dashboard examples
  - Alert rule suggestions

**Estimated Effort**: 6-8 hours

### Phase 8: Docker Hardening (Low Priority - Week 5)

**Problem**: Docker image runs as root, could be smaller

**Impact**: Low - Security and efficiency improvements

**Tasks**:
- [ ] Add non-root user to Dockerfile
  - Create `rulate` user (UID 1000)
  - Switch to non-root user before CMD
  - Update file permissions
- [ ] Evaluate Alpine base image
  - Compare `python:3.14-alpine` vs `-slim`
  - Measure image size difference
  - Test all dependencies compile on Alpine
- [ ] Enable BuildKit for better caching
  - Add BuildKit syntax to Dockerfile
  - Use cache mounts for pip/npm
- [ ] Add multi-platform build support
  - Support linux/amd64 and linux/arm64
  - Test on Apple Silicon
- [ ] Add image security scanning to CI
  - Trivy or Grype for vulnerability scanning
  - Fail build on critical vulnerabilities

**Estimated Effort**: 4-6 hours

### Phase 9: Advanced Configuration (Low Priority - Week 6)

**Problem**: Single .env file, no environment-specific configs

**Impact**: Low - Convenience improvement

**Tasks**:
- [ ] Create `config/` directory structure
  - `config/development.env`
  - `config/staging.env`
  - `config/production.env`
- [ ] Add environment selector
  - `ENV_FILE` environment variable
  - Default to `config/{ENVIRONMENT}.env`
- [ ] Add graceful shutdown handling
  - Signal handlers for SIGTERM/SIGINT
  - Close database connections
  - Finish in-flight requests
  - Log shutdown events
- [ ] Add startup banner with config summary
  - Display environment, database, features enabled
  - Warn about insecure configurations

**Estimated Effort**: 3-4 hours

## Dependencies

- **Requires**: Epic 01 (Production Ready) - Complete ✅
- **Blocks**: None (enhances existing infrastructure)
- **Related**: Epic 02 (Scale & Performance) - PostgreSQL enables scaling

## Success Metrics

- **Security**: 0 critical vulnerabilities in production
- **Reliability**: Rate limiting prevents >99% of abuse attempts
- **Scalability**: PostgreSQL supports >10,000 catalog items
- **Observability**: Mean time to detection (MTTD) < 5 minutes for errors
- **Deployability**: Database migrations complete in <30 seconds

## Open Questions

1. **Rate Limiting Strategy**: In-memory (single instance) or Redis (multi-instance)?
   - *Recommendation*: Start with in-memory, document Redis migration path
2. **Database Migration**: PostgreSQL only or support MySQL too?
   - *Recommendation*: PostgreSQL only, add MySQL if requested
3. **Observability**: Full OpenTelemetry or just Prometheus?
   - *Recommendation*: Prometheus first, OpenTelemetry as enhancement
4. **Docker User**: Always non-root or configurable?
   - *Recommendation*: Always non-root for security best practices

## Non-Goals

- **Authentication/Authorization**: Future epic (deferred until needed)
- **Advanced caching**: Covered by Epic 02 (Scale & Performance)
- **Multi-tenant support**: Out of scope for initial production
- **Custom metrics DSL**: Basic metrics sufficient for now

## References

- Production Ready epic: `docs/roadmap/01-production-ready.md`
- Code review findings: See conversation 2025-12-24
- FastAPI best practices: https://fastapi.tiangolo.com/deployment/
- Twelve-Factor App: https://12factor.net/

## Notes

This epic focuses on **completing** the production infrastructure rather than adding new features. It's about integration, hardening, and addressing gaps identified during code review. Think of it as "Production Ready Phase 2" - turning good infrastructure into great infrastructure.

Priority is weighted toward security (Phases 1-2) since those gaps pose actual risk, followed by database capabilities (Phases 4-5) that enable future scaling.
