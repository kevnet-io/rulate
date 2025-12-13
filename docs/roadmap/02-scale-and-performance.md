# Scale & Performance

> Handle growing catalogs and users

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

As catalogs grow beyond hundreds of items and concurrent users increase, the API needs to handle larger workloads efficiently. This epic addresses performance bottlenecks and adds features to prevent abuse while maintaining responsiveness.

## Success Criteria

- [ ] API handles 1000+ items per catalog without degraded response times
- [ ] Large matrix evaluations don't block the API
- [ ] Rate limiting prevents API abuse
- [ ] Pagination available on all list endpoints

## Deliverables

### Rate Limiting

**Current State**: No rate limiting.

**Goal**: Prevent API abuse while allowing legitimate use.

**Tasks**:
- [ ] Add rate limiting using `slowapi`
- [ ] Configure different limits per endpoint type (reads vs writes vs evaluations)
- [ ] Return appropriate headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
- [ ] Document rate limits in API docs

### Pagination

**Current State**: All results returned at once (fine for small datasets).

**Goal**: Efficient handling of large result sets.

**Tasks**:
- [ ] Add pagination to all list endpoints (`GET /catalogs`, `GET /items`, etc.)
- [ ] Support `?page=1&page_size=20` query params
- [ ] Return pagination metadata (total, page, page_size, total_pages)
- [ ] Add sorting options (`?sort=name&order=asc`)

### Search & Filtering

**Current State**: Client-side filtering only in Web UI.

**Goal**: Server-side search for large datasets.

**Tasks**:
- [ ] Add search to `GET /catalogs/{name}/items`
- [ ] Filter by attribute values (`?filter[color]=red`)
- [ ] Full-text search on item names
- [ ] Consider advanced query syntax for complex filters

### Caching

**Current State**: No caching; every evaluation recomputes.

**Goal**: Significant performance improvement for repeated evaluations.

**Tasks**:
- [ ] Cache compiled operator trees (avoid re-parsing rules)
- [ ] Cache evaluation results with LRU eviction
- [ ] Implement cache invalidation strategy (invalidate on rule/item change)
- [ ] Add cache metrics to health endpoint

### Async Processing

**Current State**: All operations are synchronous.

**Goal**: Large evaluations don't block the API.

**Tasks**:
- [ ] Add background job queue for large matrix evaluations
- [ ] Implement progress tracking for long-running operations
- [ ] Add WebSocket support for real-time progress updates
- [ ] Consider Celery or similar for task queue

### Database Optimization

**Current State**: SQLite works fine for small datasets.

**Goal**: Query performance at scale.

**Tasks**:
- [ ] Add indexes for common query patterns
- [ ] Optimize JSON field queries
- [ ] Implement connection pooling
- [ ] Add query performance monitoring/logging

### PostgreSQL Migration

**Current State**: SQLite only.

**Goal**: Production database option for larger deployments.

**Tasks**:
- [ ] Add PostgreSQL support via SQLAlchemy
- [ ] Create migration scripts from SQLite
- [ ] Environment-based database selection
- [ ] Configure connection pooling

## Dependencies

- [01-production-ready.md](./01-production-ready.md) - Environment configuration needed for database selection

## Open Questions

- Should pagination be opt-in (add `?paginate=true`) or opt-out for backwards compatibility?
- What cache backend should be used (in-memory, Redis)?
