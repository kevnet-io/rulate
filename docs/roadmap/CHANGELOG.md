# Changelog

All notable completed work for Rulate.

## December 2025

### Production Ready Infrastructure (Epic 01)

**Impact**: Enterprise-grade deployment capabilities

**Phase 1: Environment Configuration**
- Centralized configuration management with pydantic-settings
- Environment variable loading with validation and type safety
- Comprehensive settings for app, server, database, CORS, security, and logging
- Example `.env` files for development and production

**Phase 2: Structured Logging**
- Production-ready JSON logging with structlog
- Environment-aware formatting (JSON for production, colored text for development)
- Application context injection (app name, version, environment)
- Request/response middleware with duration tracking

**Phase 3: Health Checks**
- Kubernetes-ready health check endpoints (`/health`, `/health/ready`, `/health/live`)
- Database connectivity monitoring
- Uptime tracking and version reporting
- Proper HTTP status codes for service health (200/503)

**Phase 4: Security Hardening**
- YAML depth limiting to prevent YAML bombs (using `compose_node` for accurate depth tracking)
- File upload size validation with streaming
- Catalog name sanitization utilities (prevent path traversal)
- Comprehensive security test suite (7 tests)

**Phase 5: Docker Support**
- Multi-stage Dockerfile with optimized frontend and backend builds
- docker-compose.yml for single-command deployment
- Container health checks for orchestration platforms
- Makefile commands for Docker operations
- Production-optimized .dockerignore

**Phase 6: Documentation**
- Comprehensive deployment guide (`docs/deployment/README.md`)
- Quick start with Docker Compose
- Environment configuration reference
- Production deployment checklist
- Monitoring and observability examples

**Testing**: All 803 backend tests passing (513 unit + 290 integration)
**New Tests**: 23 tests added (7 security + 9 config + 7 health)

See Epic 01 in `docs/roadmap/01-production-ready.md` for full details.

### Gender-Agnostic Wardrobe v2 with Coverage-Layer Modeling

**Impact**: Production-ready example domain with realistic complexity

- **New dimension type**: `part_layer_list` for granular coverage-layer modeling
- **PartLayerConflictOperator**: Phasing detection prevents impossible layering configurations
- **53 diverse items**: Gender-agnostic catalog (masculine, feminine, unisex clothing)
- **22 body parts vocabulary**: Precise coverage modeling (upper_arm, lower_leg, chest, etc.)
- **Clear separation**: Physical compatibility (pairwise) vs aesthetic compatibility (cluster)
- **Modernized storage**: JSON export format replaces 8 YAML files
- **Simplified seeding**: 124-line script with single API call (was 228 lines, 26+ calls)
- **Comprehensive tests**: 312 new tests (161 operator, 151 dimension, 32 integration)
- **Pattern documentation**: Reusable coverage-layer conflict pattern guide

Total: 1,833 tests passing (780 backend + 876 frontend + 177 E2E)

See [coverage-layer-conflicts.md](../patterns/coverage-layer-conflicts.md) for the reusable pattern.

### Comprehensive Test Suite

**Impact**: High confidence in system reliability

- 480 backend tests (94% coverage) across all core modules
- 671 frontend tests (100% production code coverage)
- 72 E2E tests with Playwright across 3 browsers (Chromium, Firefox, WebKit)
- **Total: 1,151+ tests** ensuring system reliability

### Import/Export Functionality

**Impact**: Bulk data backup and migration

- 14 API endpoints for data import/export
- Web UI page for bulk operations
- JSON format support with validation
- Automatic dependency handling for imports

### UX Polish

**Impact**: Replaced all browser dialogs with accessible custom components

- **Toast notifications** - Custom system with 4 types (success, error, warning, info), auto-dismiss, stacking
- **Modal dialogs** - Accessible modals with focus trap, keyboard nav, contextual confirmations
- **Loading states** - Spinner component and skeleton loaders on all list pages
- **Empty states** - Helpful empty states with icons and CTAs on all list pages
- **Tooltips** - Reusable tooltip component for inline help
- **Form validation** - FormField component and comprehensive validation utilities
- **Unsaved changes** - Warning before navigation with unsaved form data
- **Enhanced rule editor** - Operator documentation sidebar, search, templates (18 presets)
- **Operator registry** - 17 operators fully documented with examples and parameters

Zero browser `alert()` or `confirm()` calls remaining. WCAG 2.1 AA compliant.

See [UX_POLISH_SUMMARY.md](../UX_POLISH_SUMMARY.md) for full details.

### Developer Experience Infrastructure

**Impact**: Automated quality gates and contributor onboarding

- **GitHub Actions CI/CD** - Automated testing with Python 3.14, frontend unit tests, E2E tests (9 parallel jobs)
- **Pre-commit hooks** - Black, Ruff, Mypy, Prettier, ESLint with auto-fix
- **GitHub templates** - Bug reports, feature requests, and PR templates
- **CONTRIBUTING.md** - Comprehensive contributor guide with setup, workflow, and coding standards
- **Dependabot** - Automated weekly dependency updates for Python, npm, and GitHub Actions
- **VS Code integration** - Shared settings and 15+ recommended extensions
- **EditorConfig** - Consistent formatting across all editors
- **Code of Conduct** - Contributor Covenant 2.0 for open source collaboration
- **Build badges** - Test status and version badges in README
