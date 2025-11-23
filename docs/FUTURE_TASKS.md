# Future Tasks & Enhancements

This document tracks planned enhancements and nice-to-have features for Rulate. The core functionality is complete and production-ready; these tasks represent opportunities for improvement and polish.

---

## Priority 1: Testing & Quality Assurance

### Automated API Testing
**Status**: Not implemented
**Effort**: Medium
**Value**: High

- [ ] Write automated tests for all 28 API endpoints
- [ ] Test CRUD operations for each resource type
- [ ] Test error cases and validation failures
- [ ] Test evaluation endpoints with various rule combinations
- [ ] Test cluster evaluation and relationships
- [ ] Achieve 80%+ coverage on API routes

**Current State**: Manual testing via `/docs` interface and integration testing with example data.

**Implementation Notes**:
- Use pytest with httpx for async testing
- Create test fixtures for schemas, rulesets, catalogs
- Test database transactions and rollbacks
- Verify response status codes and schemas

---

### Web UI Component Tests
**Status**: Not implemented
**Effort**: Medium
**Value**: Medium

- [ ] Set up Vitest or Jest for Svelte component testing
- [ ] Test form validation logic
- [ ] Test dynamic dimension/rule builders
- [ ] Test API client integration
- [ ] Mock API responses for isolated testing

**Current State**: Manual testing in development and browser.

**Implementation Notes**:
- Use @testing-library/svelte
- Test user interactions and state management
- Mock API calls with MSW or similar
- Test accessibility features

---

### End-to-End Testing
**Status**: Not implemented
**Effort**: High
**Value**: Medium

- [ ] Set up Playwright or Cypress
- [ ] Write E2E tests for critical user flows:
  - Create schema → Create catalog → Add items → Evaluate
  - Create ruleset → Run matrix evaluation
  - Cluster finding workflow
- [ ] Test cross-browser compatibility
- [ ] Test mobile responsive layouts

**Current State**: Manual testing of user workflows.

---

### Integration Tests
**Status**: Not implemented
**Effort**: Medium
**Value**: High

- [ ] End-to-end workflow tests (file import → evaluation → export)
- [ ] Test CLI commands with real files
- [ ] Test API + database interactions
- [ ] Test core engine with various rule combinations
- [ ] Expand wardrobe example test coverage

**Current State**: Basic integration testing with wardrobe example, no automated tests.

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

### File Upload/Download
**Status**: Not implemented
**Effort**: Low
**Value**: Low

- [ ] Add file upload for schemas, rulesets, catalogs
- [ ] Add export buttons that download YAML/JSON files
- [ ] Drag-and-drop file upload zones
- [ ] File validation before upload
- [ ] Progress indicators for large files

**Current State**: Copy/paste JSON works, but not user-friendly for non-technical users.

**Implementation Notes**:
- Use `js-yaml` for YAML parsing in browser
- Validate files client-side before API call
- Provide clear error messages for invalid files

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

1. **Testing** (Priority 1) - Foundation for quality
   - Start with API tests
   - Add integration tests
   - Web UI tests last

2. **DevOps** (Priority 3) - Enable easy deployment
   - Docker first
   - Health checks
   - Deployment guide

3. **UX Polish** (Priority 2) - Improve user experience
   - Toast notifications
   - Modal dialogs
   - File upload/download

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
