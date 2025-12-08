# Future Tasks & Enhancements

This document tracks planned enhancements and nice-to-have features for Rulate. The core functionality is complete and production-ready; these tasks represent opportunities for improvement and polish.

## Recent Completions (December 2025)

The following major tasks have been completed:

### ✅ Comprehensive Test Suite
- **480 backend tests** (94% coverage) across all core modules
- **671 frontend tests** (100% production code coverage)
- **72 E2E tests** with Playwright across 3 browsers
- **Total: 1,151 tests** ensuring system reliability

### ✅ Import/Export Functionality
- **14 API endpoints** for data import/export
- **Web UI page** for bulk operations
- **JSON format** support with validation
- **Backup and migration** workflows

---

## Priority 1: Testing & Quality Assurance

### ✅ COMPLETED: Comprehensive Test Suite
**Status**: ✅ **COMPLETE**
**Completion Date**: December 2025

**Backend Testing** - FULLY IMPLEMENTED:
- [x] 480 automated tests across 11 test files
- [x] 94% overall code coverage
- [x] All core modules tested (models, operators, evaluators, loaders, exporters, CLI)
- [x] Test CRUD operations for each resource type
- [x] Test error cases and validation failures
- [x] Test evaluation endpoints with various rule combinations
- [x] Test cluster evaluation and relationships
- [x] Comprehensive test fixtures and shared configuration

**Frontend Testing** - FULLY IMPLEMENTED:
- [x] 671 tests across 22 test files
- [x] 100% production code coverage (API client, forms, utilities)
- [x] Vitest 4.0 with @vitest/coverage-v8
- [x] @testing-library/svelte for component testing
- [x] All 42 API endpoints tested in client
- [x] Form validation logic for all 6 dimension types (37 tests)
- [x] UI component tests (Badge, Button, Card, Skeleton, Navigation)
- [x] All 19 page components tested

**E2E Testing** - FULLY IMPLEMENTED:
- [x] Playwright setup with 72 E2E tests
- [x] Cross-browser testing (Chromium, Firefox, WebKit)
- [x] Critical user flows:
  - [x] Schema management workflow
  - [x] Catalog and item CRUD operations
  - [x] Interactive compatibility explorer
  - [x] Navigation and routing
- [x] Mobile responsive layout testing

**Test Infrastructure**:
- [x] pytest with coverage reporting
- [x] Vitest 4.0 for frontend unit tests
- [x] Playwright for E2E testing
- [x] happy-dom environment for Svelte 5
- [x] Comprehensive test fixtures and utilities
- [x] Test code excluded from coverage metrics (standard practice)

**Total Achievement**: 1,151 tests with excellent coverage across all layers.

---

## Priority 2: User Experience Polish

### Toast Notifications
**Status**: Not implemented (using browser alerts)
**Effort**: Low
**Value**: Medium

- [ ] Replace browser `alert()` calls with toast notifications
- [ ] Implement toast component (success, error, warning, info)
- [ ] Add auto-dismiss with configurable timeout
- [ ] Position toasts appropriately (top-right recommended)
- [ ] Support stacking multiple toasts

**Current State**: Using `alert()` for error messages and confirmations.

**Recommended Library**: svelte-french-toast or build custom with Tailwind

---

### Modal Confirmation Dialogs
**Status**: Partial (using browser confirm)
**Effort**: Low
**Value**: Medium

- [ ] Replace browser `confirm()` with custom modal
- [ ] Create reusable Modal component
- [ ] Add proper accessibility (focus trap, ESC to close, ARIA labels)
- [ ] Improve delete confirmations with item details
- [ ] Add confirmation for destructive actions

**Current State**: Using browser `confirm()` for delete operations.

---

### Visual Rule Builder
**Status**: Partial (JSON editor only)
**Effort**: High
**Value**: Medium

- [ ] Design drag-and-drop interface for building conditions
- [ ] Operator palette with descriptions
- [ ] Visual tree representation of nested conditions
- [ ] Real-time validation and preview
- [ ] Toggle between visual and JSON modes
- [ ] Template/preset conditions

**Current State**: JSON textarea editor with syntax highlighting would be helpful first step.

**Implementation Notes**:
- Consider libraries like react-flow or build custom with Svelte
- Show operator documentation inline
- Validate as user builds
- Generate JSON from visual representation

---

### ✅ COMPLETED: Import/Export Functionality
**Status**: ✅ **COMPLETE**
**Completion Date**: December 2025

**API Endpoints** - FULLY IMPLEMENTED:
- [x] 14 import/export endpoints in `api/routers/import_export.py`
- [x] Export individual resources (schemas, rulesets, cluster-rulesets, catalogs)
- [x] Export all data types in single request
- [x] Import with automatic dependency validation
- [x] Import individual or bulk data
- [x] JSON format support

**Web UI** - FULLY IMPLEMENTED:
- [x] Dedicated `/import-export` page
- [x] File upload for JSON imports
- [x] Download buttons for JSON exports
- [x] Export all data or individual resource types
- [x] Import validation with error reporting
- [x] Clear user feedback for success/failure

**Features**:
- [x] Backup and restore workflows
- [x] Data migration between instances
- [x] Dependency handling (e.g., catalogs reference schemas)
- [x] Comprehensive error messages

**Note**: Drag-and-drop and YAML format could be added as enhancements, but JSON upload/download is fully functional.

---

## Priority 3: DevOps & Deployment

### Docker Configuration
**Status**: Not implemented
**Effort**: Low
**Value**: High

- [ ] Create `Dockerfile` for API server
- [ ] Create `Dockerfile` for Web UI
- [ ] Create `docker-compose.yml` for full stack
- [ ] Document environment variables
- [ ] Add health checks to containers
- [ ] Optimize image sizes (multi-stage builds)
- [ ] Create docker-compose for development

**Benefits**: Easy deployment, consistent environments, simplified setup.

---

### Health Check Endpoint
**Status**: Not implemented
**Effort**: Low
**Value**: Medium

- [ ] Add `GET /health` endpoint
- [ ] Check database connectivity
- [ ] Return service status and version
- [ ] Add readiness probe (for Kubernetes)
- [ ] Add liveness probe

**Current State**: No health check endpoint.

**Implementation**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": "connected"  # Test DB connection
    }
```

---

### Advanced Logging
**Status**: Basic logging only
**Effort**: Low
**Value**: Medium

- [ ] Structured logging (JSON format)
- [ ] Log levels per module
- [ ] Request/response logging
- [ ] Error tracking integration (Sentry, etc.)
- [ ] Performance metrics logging
- [ ] Log rotation and retention

**Current State**: Basic print/logging statements.

**Recommended**: Use `structlog` for structured logging.

---

### Environment Configuration
**Status**: Basic, no .env support
**Effort**: Low
**Value**: Medium

- [ ] Add `.env` file support
- [ ] Environment-specific configurations (dev, staging, prod)
- [ ] Secure secret management
- [ ] Database URL configuration
- [ ] CORS configuration
- [ ] API key authentication (if needed)

**Current State**: Hardcoded configuration values.

**Recommended**: Use `pydantic-settings` for config management.

---

### Deployment Guide
**Status**: Basic instructions only
**Effort**: Low
**Value**: Medium

- [ ] Write comprehensive deployment guide
- [ ] Document cloud deployment options (AWS, GCP, Azure, DigitalOcean)
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline examples (GitHub Actions)
- [ ] Production checklist
- [ ] Monitoring and observability setup
- [ ] Backup and restore procedures

**Current State**: Basic "run uvicorn" and "npm run dev" in README.

---

## Priority 4: Features & Enhancements

### API Features

#### Rate Limiting
**Effort**: Low
**Value**: Medium

- [ ] Add rate limiting to API endpoints
- [ ] Different limits per endpoint type
- [ ] Return appropriate headers (X-RateLimit-*)
- [ ] Document rate limits

**Recommended**: Use `slowapi` (FastAPI rate limiting)

---

#### API Versioning
**Effort**: Low
**Value**: Low

- [ ] Prepare for API v2 if needed
- [ ] Version in URL path already (`/api/v1/`)
- [ ] Document deprecation policy

**Current State**: All endpoints under `/api/v1/` already.

---

#### Pagination
**Effort**: Medium
**Value**: Medium

- [ ] Add pagination to list endpoints
- [ ] Support `?page=1&page_size=20` query params
- [ ] Return pagination metadata
- [ ] Add sorting options

**Current State**: All results returned at once (fine for small datasets).

---

#### Search & Filtering
**Effort**: Medium
**Value**: Medium

- [ ] Add search to GET /catalogs/{name}/items
- [ ] Filter by attribute values
- [ ] Full-text search on item names
- [ ] Advanced query syntax

**Current State**: Client-side filtering only in Web UI.

---

### Core Engine Features

#### Caching
**Effort**: Medium
**Value**: Medium

- [ ] Cache evaluation results
- [ ] Cache compiled operator trees
- [ ] LRU cache for frequently evaluated pairs
- [ ] Cache invalidation strategy

**Benefits**: Significant performance improvement for repeated evaluations.

---

#### Scoring System
**Effort**: High
**Value**: High

Replace boolean compatibility with confidence scores.

- [ ] Define scoring algorithm
- [ ] Update operators to return scores
- [ ] Weighted rule importance
- [ ] Aggregate scores across rules
- [ ] Update API responses to include scores

**Current State**: Binary compatible/incompatible only.

---

#### Context/Occasion Support
**Effort**: Medium
**Value**: High

Allow rules to reference context (weather, occasion, etc.)

- [ ] Define Context model
- [ ] Add context to evaluation requests
- [ ] Context-aware operators
- [ ] Context filtering in UI

**Example**:
```yaml
condition:
  context_match:
    field: "season"
    context_key: "weather"
```

---

#### Custom Operators
**Effort**: Medium
**Value**: Medium

- [ ] Plugin system for custom operators
- [ ] Operator registration API
- [ ] Documentation for writing operators
- [ ] Example custom operators

**Current State**: Must edit `operators.py` to add operators.

---

### Web UI Features

#### Bulk Operations
**Effort**: Medium
**Value**: Low

- [ ] Bulk delete items
- [ ] Bulk edit attributes
- [ ] Import multiple items from CSV
- [ ] Export catalog to CSV

---

#### Saved Queries/Filters
**Effort**: Medium
**Value**: Low

- [ ] Save frequently used evaluations
- [ ] Named presets
- [ ] Share saved queries

---

#### User Preferences
**Effort**: Low
**Value**: Low

- [ ] Dark mode toggle
- [ ] Default output format
- [ ] UI preferences (density, etc.)
- [ ] Persistent settings in localStorage

---

#### Visualization Improvements
**Effort**: Medium
**Value**: Medium

- [ ] Graph visualization of compatibility network
- [ ] Cluster visualization with D3.js
- [ ] Heatmap for matrix view
- [ ] Export visualizations as images

---

## Priority 5: Documentation

### API Documentation Improvements
**Effort**: Low
**Value**: Medium

- [ ] Add more request/response examples to OpenAPI
- [ ] Document error codes and messages
- [ ] Add authentication docs (if implemented)
- [ ] Interactive examples in docs

**Current State**: Auto-generated OpenAPI docs are good but could be enhanced.

---

### User Guide
**Effort**: Medium
**Value**: High

- [ ] Step-by-step tutorials
- [ ] Video walkthroughs
- [ ] Common use cases beyond wardrobe
- [ ] Troubleshooting guide
- [ ] FAQ

**Current State**: README has quick start, but lacks detailed tutorials.

---

### Developer Guide
**Effort**: Medium
**Value**: Medium

- [ ] Architecture deep-dive
- [ ] Code walkthrough
- [ ] Contribution guidelines
- [ ] Coding standards
- [ ] Release process

**Current State**: CLAUDE.md has some info, but needs expansion.

---

### Domain Examples
**Effort**: Medium
**Value**: High

Create example configurations for other domains:

- [ ] Recipe ingredient compatibility
- [ ] Software dependency compatibility
- [ ] Course prerequisite chains
- [ ] Furniture arrangement rules
- [ ] Team member skill matching

**Benefits**: Demonstrate domain-agnostic nature, provide templates.

---

## Priority 6: Performance & Scalability

### Database Optimization
**Effort**: Medium
**Value**: Medium

- [ ] Add indexes for common queries
- [ ] Optimize JSON queries
- [ ] Connection pooling
- [ ] Query performance monitoring

**Current State**: SQLite works fine for small datasets, may need PostgreSQL for scale.

---

### Async Processing
**Effort**: High
**Value**: Medium

- [ ] Background job queue for large evaluations
- [ ] Progress tracking for matrix calculations
- [ ] WebSocket for real-time updates
- [ ] Celery or similar for task queue

**Benefits**: Better UX for large catalogs.

---

### Database Migration to PostgreSQL
**Effort**: Medium
**Value**: Medium (for production)

- [ ] PostgreSQL support
- [ ] Migration scripts from SQLite
- [ ] Environment-based DB selection
- [ ] Connection pooling with SQLAlchemy

**Current State**: SQLite only.

---

## Priority 7: Security

### Authentication & Authorization
**Effort**: High
**Value**: High (for multi-user)

- [ ] User registration and login
- [ ] JWT token authentication
- [ ] Role-based access control (RBAC)
- [ ] Catalog ownership and permissions
- [ ] API key authentication

**Current State**: No authentication (single-user system).

---

### Input Sanitization
**Effort**: Low
**Value**: High

- [ ] Audit all input validation
- [ ] SQL injection prevention (already handled by SQLAlchemy)
- [ ] XSS prevention in Web UI
- [ ] YAML/JSON bomb prevention
- [ ] File size limits

**Current State**: Basic Pydantic validation, but needs security audit.

---

### HTTPS/TLS
**Effort**: Low
**Value**: High (for production)

- [ ] SSL/TLS configuration guide
- [ ] Certificate management
- [ ] Redirect HTTP to HTTPS

**Current State**: Development uses HTTP only.

---

## Implementation Priorities

### Recommended Order

1. ~~**Testing** (Priority 1)~~ - ✅ **COMPLETE**
   - ~~Start with API tests~~ ✅
   - ~~Add integration tests~~ ✅
   - ~~Web UI tests last~~ ✅

2. **DevOps** (Priority 3) - Enable easy deployment (NEXT PRIORITY)
   - Docker first
   - Health checks
   - Deployment guide

3. **UX Polish** (Priority 2) - Improve user experience
   - Toast notifications
   - Modal dialogs
   - ~~File upload/download~~ ✅ **COMPLETE** (Import/Export implemented)

4. **Documentation** (Priority 5) - Help users succeed
   - User guide
   - Domain examples

5. **Features** (Priority 4) - Enhance capabilities
   - Caching for performance
   - Scoring system
   - Context support

6. **Security** (Priority 7) - For production deployment
   - Input sanitization audit
   - HTTPS setup
   - Authentication (if multi-user needed)

7. **Scalability** (Priority 6) - As needed
   - PostgreSQL migration
   - Async processing

---

## Won't Do (Scope Creep Prevention)

The following were considered but deemed out of scope:

- ❌ Mobile native apps (Web UI is responsive)
- ❌ Real-time collaborative editing
- ❌ Machine learning for rule suggestions
- ❌ Natural language rule parsing
- ❌ Integration with external services (keep it self-contained)
- ❌ Built-in image storage for items
- ❌ Social features (sharing, comments, likes)

---

## Contributing

Want to tackle one of these tasks? Great!

1. Check if there's an issue for it (create one if not)
2. Comment on the issue to claim it
3. Follow the development setup in `docs/CLAUDE.md`
4. Submit a PR with tests and documentation
5. Reference this document in your PR description

---

## Notes

- Tasks marked with ⭐ are particularly valuable for first-time contributors
- Effort estimates: Low (< 1 day), Medium (1-3 days), High (3+ days)
- Value estimates are subjective and based on typical use cases
- Priorities may shift based on user feedback and real-world usage

Last Updated: November 2025
