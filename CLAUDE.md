# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rulate is a generic, programmable rule-based comparison engine for evaluating and classifying relationships between pairs of objects. The system uses declarative YAML/JSON schemas and rules to determine compatibility between items in a catalog.

**Initial use case**: Wardrobe compatibility checking (determining which clothing items can be worn together), but the engine is designed to be domain-agnostic.

## Quick Reference

**Common Commands:**
- `make install` - Install all dependencies (backend + frontend + hooks)
- `make dev-backend` - Start API server on http://localhost:8000
- `make dev-frontend` - Start web UI on http://localhost:5173
- `make format` - Auto-fix all formatting issues (modifies files)
- `make check` - Run all checks except e2e (fast, CI-safe, read-only, ~30-40s)
- `make check-all` - Run all checks including e2e (comprehensive, ~90s)
- `make test` - Run all unit tests (backend + frontend, ~15-20s)
- `make test-backend` - Run backend tests only (~10s)
- `make test-frontend` - Run frontend unit tests only (~5s)

**Workflow:**
1. **During development:** `make format` (auto-fix code style)
2. **Before committing:** `make check` (verify all checks pass except e2e)
3. **Commit:** Pre-commit hooks run automatically
4. **Push:** CI runs all checks in parallel (9 fine-grained jobs)

For all available commands: `make` or `make help`

## Architecture

Rulate has a three-layer architecture:

### 1. Core Engine (`rulate/`)
The domain-agnostic evaluation engine that processes schemas, rules, and catalogs.

**Key concepts:**
- **Schema**: Defines the dimension space (what attributes objects can have). Supports 6 types: string, integer, float, boolean, enum, list.
- **RuleSet**: Contains compatibility rules. Two rule types:
  - **Exclusion rules**: Items are incompatible if condition is TRUE
  - **Requirement rules**: Items are compatible only if condition is TRUE
- **Catalog**: Collection of items with attributes validated against a schema
- **Operators**: Building blocks for rule conditions (equals, abs_diff, has_different, all/any/not logical operators)

**Evaluation flow:**
1. Load schema, ruleset, and catalog (via `rulate.utils.loaders`)
2. Validate items against schema dimensions
3. For each pair of items:
   - Apply all exclusion rules (any fail → incompatible)
   - Apply all requirement rules (all must pass → compatible)
4. Return `ComparisonResult` with compatibility decision and rule evaluations

**Key modules:**
- `rulate/models/` - Pydantic models for all data structures
- `rulate/engine/operators.py` - Operator implementations for rule conditions (pairwise and cluster)
- `rulate/engine/condition_evaluator.py` - Parses and evaluates pairwise condition dictionaries
- `rulate/engine/cluster_condition_evaluator.py` - Parses and evaluates cluster condition dictionaries
- `rulate/engine/evaluator.py` - Main pairwise evaluation orchestrator (evaluate_pair, evaluate_matrix, evaluate_item_against_catalog)
- `rulate/engine/cluster_evaluator.py` - Cluster finding engine using Bron-Kerbosch algorithm
- `rulate/utils/` - YAML/JSON loaders and exporters

**Cluster Mechanism:**
Rulate includes a sophisticated cluster mechanism for finding compatible sets of items beyond pairwise compatibility.

- **Clusters**: Sets of items where all pairs are mutually compatible AND the set satisfies cluster-level rules
- **Two-Level Rule System**:
  1. **Pairwise RuleSet**: Determines which items CAN go together (builds compatibility graph)
  2. **ClusterRuleSet**: Determines which sets FORM valid clusters (set-level constraints)
- **Algorithm**: Bron-Kerbosch with pivoting for finding all maximal cliques
- **Cluster Operators** (8 set-level operators in addition to pairwise operators):
  - `min_cluster_size`, `max_cluster_size` - Size constraints
  - `unique_values` - Ensure field uniqueness across cluster
  - `has_item_with` - Require items matching criteria
  - `count_by_field` - Count distinct field values
  - `formality_range` - Domain-specific formality consistency
  - `all`, `any`, `not` - Logical operators for cluster conditions
- **Relationships**: Automatically detects subset, superset, and overlapping patterns between clusters

### 2. REST API (`api/`)
FastAPI backend with SQLite persistence for managing schemas, rulesets, and catalogs via HTTP.

**Database architecture:**
- SQLAlchemy ORM with SQLite (`api/database/models.py`)
- Tables: `schemas`, `rulesets`, `cluster_rulesets`, `catalogs`, `items`
- Complex fields (dimensions, rules, attributes) stored as JSON in TEXT columns
- Uses getter/setter methods (`get_dimensions()`, `set_dimensions()`) not properties to avoid SQLAlchemy metadata conflicts
- `ClusterRuleSetDB` model references both schema and pairwise ruleset

**API structure:**
- `api/main.py` - FastAPI app setup with lifespan events
- `api/routers/` - Endpoint implementations (schemas, rulesets, catalogs, evaluation, clusters, import_export)
- `api/models/schemas.py` - Pydantic request/response models (distinct from core models)
- `api/database/connection.py` - Session management with `get_db()` dependency
- `api/routers/clusters.py` - Cluster evaluation endpoint (`POST /evaluate/clusters`)
- `api/routers/import_export.py` - Bulk import/export endpoints for data backup and migration

**Important conversion pattern:**
The API routers convert between database models (SQLAlchemy) and core Rulate models (Pydantic) using helper functions like `db_to_rulate_schema()`, `db_to_rulate_catalog()` in `api/routers/evaluation.py`.

### 3. CLI Tool (`rulate/cli.py`)
Click-based command-line interface with three command groups:
- `validate` - Validate schema/rules/catalog files
- `evaluate` - Run compatibility evaluations (pair, matrix, item)
- `show` - Display information about schemas and catalogs

### 4. Web UI (`web/`)
SvelteKit 2.0 frontend with TypeScript providing interactive visualization and management.

**Technology stack:**
- SvelteKit 2.0 with Svelte 5 syntax (runes, event handlers)
- TypeScript for type safety
- Tailwind CSS for styling with custom design system
- Vite dev server with API proxy

**Key pages:**
- `web/src/routes/+page.svelte` - Dashboard with overview statistics
- `web/src/routes/schemas/` - Schema list and detail views
- `web/src/routes/schemas/new/` - Schema creation form with dynamic dimension management
- `web/src/routes/rulesets/` - RuleSet list and detail views
- `web/src/routes/rulesets/new/` - RuleSet creation form with rule builder
- `web/src/routes/catalogs/` - Catalog list, detail, and item views
- `web/src/routes/catalogs/new/` - Catalog creation form
- `web/src/routes/catalogs/[name]/items/new/` - Item creation form with schema-driven fields
- `web/src/routes/catalogs/[name]/items/[itemId]/` - Item detail view
- `web/src/routes/catalogs/[name]/items/[itemId]/edit/` - Item edit form
- `web/src/routes/explore/+page.svelte` - Interactive compatibility explorer
- `web/src/routes/matrix/+page.svelte` - Compatibility matrix visualization
- `web/src/routes/import-export/+page.svelte` - Bulk import/export page for data backup and migration

**Important components:**
- `web/src/lib/api/client.ts` - TypeScript API client with type definitions
- `web/src/lib/components/Navigation.svelte` - Main navigation bar
- `web/src/lib/components/ui/` - Reusable UI components (Button, Card, Badge, etc.)

**Svelte 5 syntax notes:**
- Event handlers use `onclick` prop instead of `on:click` directive
- Button component is polymorphic - renders `<a>` when `href` prop provided, `<button>` otherwise
- Button component accepts `type` prop ('button'|'submit'|'reset') to control form submission behavior
- Use `{@const}` blocks inside conditional/loop blocks for derived values
- Object mutations don't trigger reactivity - reassign the object to trigger updates: `obj = obj`

## Development Commands

### Quick Start

```bash
# First time setup - install everything
make install

# Start development servers
make dev-backend  # Terminal 1: API server on http://localhost:8000
make dev-frontend # Terminal 2: Web UI on http://localhost:5173
```

### Installation

```bash
# Install all dependencies (backend + frontend + pre-commit hooks)
make install

# Or install components separately:
make install-backend   # Python dependencies with uv
make install-frontend  # Node.js dependencies
make install-hooks     # Pre-commit hooks
```

This command:
- Creates a virtual environment in `.venv/`
- Installs all project dependencies
- Installs all dev dependencies (pytest, black, ruff, mypy, pre-commit, etc.)
- Sets up pre-commit hooks to automatically run code quality checks before each commit
- Installs frontend dependencies for ESLint and testing

**IMPORTANT:** Pre-commit hooks are REQUIRED before committing. They run automatically on `git commit`.

### Code Quality Workflow

Rulate uses a **two-tier workflow** for code quality:

#### 1. Auto-Fix Commands (Modify Files)

Use these when actively developing to automatically fix formatting issues:

```bash
# Format all code (Python + frontend)
make format

# Format only backend (black + ruff --fix)
make format-backend

# Format only frontend (prettier)
make format-frontend
```

#### 2. Check Commands (Read-Only, CI-Safe)

Use these before committing or in CI to verify code quality without modifying files:

```bash
# Check everything except e2e (fast ~30-40s) - RECOMMENDED before pushing
make check

# Check all backend checks (lint + typecheck + test)
make check-backend

# Check all frontend checks (format + lint + typecheck + tests + e2e)
make check-frontend

# Check everything including e2e (comprehensive ~90s)
make check-all

# Run pre-commit hooks on all files
make pre-commit
```

**Best Practice:**
1. During development: `make format` to auto-fix issues
2. Before committing: `make check` to verify all checks pass (fast, excludes e2e)
3. Commit triggers pre-commit hooks automatically
4. CI runs all checks in parallel (9 fine-grained jobs with Python 3.14)

### Testing

```bash
# All unit tests (backend + frontend ~15-20s)
make test              # Run all unit tests (backend 697 + frontend 671)
make test-backend      # Run backend tests only (697 tests ~10s)
make test-frontend     # Run frontend unit tests only (671 tests ~5s)
make test-cov          # Run backend tests with coverage report
make test-e2e          # Run E2E tests (72 tests across 3 browsers ~60s)

# Backend unit tests (core engine - 480 tests)
uv run pytest tests/unit/                    # Unit tests only
uv run pytest tests/unit/ --cov=rulate       # With coverage (94%)
uv run pytest tests/unit/test_schema.py      # Specific test file
uv run pytest tests/unit/test_schema.py::TestSchema::test_create_simple_schema  # Specific test

# Backend integration tests (API layer - 217 tests)
uv run pytest tests/integration/             # Integration tests only
uv run pytest tests/integration/ --cov=api   # API coverage (88.5%)
uv run pytest tests/integration/test_api_schemas.py  # Specific API test file

# Full backend coverage
uv run pytest --cov=rulate --cov=api --cov-report=html

# Frontend test commands:
cd web && npm test
cd web && npm run test:ui          # Interactive test UI
cd web && npm run test:coverage    # With coverage report
cd web && npm run test:e2e         # E2E tests (playwright)
```

Alternatively, activate the virtual environment first:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pytest                     # Run all backend tests
pytest tests/unit/         # Unit tests only
pytest tests/integration/  # Integration tests only
```

### Code Coverage & Codecov

Rulate uses [Codecov](https://codecov.io) for coverage tracking and reporting. Coverage reports are automatically uploaded to Codecov during CI runs.

**Coverage configuration** (`codecov.yml`):
- **Project coverage**: Tracks overall project coverage trends
- **Patch coverage**: Set to **informational mode** - shows coverage metrics for new code in PRs without blocking merges

This configuration allows visibility into test coverage while learning coverage practices. The patch check can be made required later by changing `informational: true` to `informational: false` in `codecov.yml`.

**Local coverage reports:**
```bash
# Backend coverage (HTML report in htmlcov/)
make test-cov

# Frontend coverage (HTML report in web/coverage/)
cd web && npm run test:coverage
```

### Individual Tools

While `make` targets are recommended, you can run individual tools:

```bash
# Python formatting
uv run black .

# Python linting (check only)
uv run ruff check .

# Python linting (auto-fix)
uv run ruff check . --fix

# Python type checking (core only - API excluded due to SQLAlchemy typing complexity)
uv run mypy rulate

# Frontend formatting (check)
cd web && npm run format:check

# Frontend formatting (auto-fix)
cd web && npm run format

# Frontend linting (check)
cd web && npm run lint

# Frontend linting (auto-fix)
cd web && npm run lint:fix

# Frontend type checking
cd web && npm run typecheck
```

### Development Servers

For development, run two separate servers for optimal developer experience (hot module reloading):

```bash
# Terminal 1: Backend API on port 8000
make dev-backend
# Interactive API docs: http://localhost:8000/docs

# Terminal 2: Frontend with HMR on port 5173
make dev-frontend

# Or use underlying commands:
uv run uvicorn api.main:app --reload
cd web && npm run dev
```

**Development setup:**
- Frontend (Vite): `http://localhost:5173` - proxies `/api/*` requests to backend
- Backend (FastAPI): `http://localhost:8000` - serves API only
- CORS enabled for cross-origin requests between the two servers

### Production Build & Serve

For production, the FastAPI server serves both the API and the built frontend as a unified application:

```bash
# Build frontend and start unified server
make serve-production

# Or manually:
cd web && npm run build
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000

# Access at: http://localhost:8000
```

**Production setup:**
- Single server on `http://localhost:8000` serves both API and frontend
- Frontend built as static assets in `web/build/` directory
- No CORS needed (same-origin requests)
- API available at `/api/v1/*` routes
- All other routes serve the SvelteKit SPA

**To just build the frontend without serving:**
```bash
make build-frontend
# Output: web/build/
```

### Using the CLI

```bash
# Validate files
uv run rulate validate schema examples/wardrobe/schema.yaml
uv run rulate validate catalog examples/wardrobe/catalog.yaml --schema examples/wardrobe/schema.yaml

# Evaluate compatibility
uv run rulate evaluate pair shirt_001 pants_002 \
  --catalog examples/wardrobe/catalog.yaml \
  --rules examples/wardrobe/rules.yaml \
  --schema examples/wardrobe/schema.yaml

# Generate compatibility matrix
uv run rulate evaluate matrix \
  --catalog examples/wardrobe/catalog.yaml \
  --rules examples/wardrobe/rules.yaml \
  --format summary  # or json, yaml, csv
```

### Cleaning Build Artifacts

```bash
# Clean all build artifacts
make clean

# Clean only backend (__pycache__, .pytest_cache, .mypy_cache, htmlcov, etc.)
make clean-backend

# Clean only frontend (.svelte-kit, build, coverage, playwright-report)
make clean-frontend

# Clean development databases
make clean-db
```

### Pre-Commit Hooks

Pre-commit hooks run automatically on `git commit` and include:
- **Python:** black (formatting), ruff --fix (linting), mypy (type checking - core only)
- **Frontend:** prettier (formatting), ESLint (linting)
- **General:** YAML/JSON validation, trailing whitespace, end-of-file fixes

```bash
# Run all hooks manually
make pre-commit
# Or: uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run black --all-files
uv run pre-commit run mypy --all-files
```

**IMPORTANT:**
- If you bypass hooks with `git commit --no-verify`, CI will fail
- Run `make check` before pushing to verify all checks pass (or `make check-all` for comprehensive e2e checks)
- The `.claude/settings.json` file includes a Stop hook for automated pre-commit checking

### Type Checking Note

- Core engine (`rulate/`) is fully type-checked with mypy (strict mode)
- API layer (`api/`) is temporarily excluded due to SQLAlchemy Column typing complexity
- This is pragmatic - core business logic is type-safe while API layer needs future improvements

### Git Commit Messages

All commits should include the following footer to attribute Claude Code assistance:

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Example commit:**
```bash
git commit -m "Add new cluster operator for size constraints

Implements MinClusterSizeOperator to enforce minimum cluster sizes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## Important Implementation Details

### Rule Condition Language
Rules use a declarative condition language expressed as nested dictionaries:
```python
# Example: Items incompatible if same body_zone and NOT different layers
condition = {
    "all": [
        {"equals": {"field": "body_zone"}},
        {"not": {"has_different": {"field": "layer"}}}
    ]
}
```

Operators are registered in `OPERATOR_REGISTRY` and instantiated dynamically by `condition_evaluator.py`.

### Adding New Operators
1. Create operator class in `rulate/engine/operators.py` inheriting from `Operator`
2. Implement `evaluate(item1: Item, item2: Item) -> Tuple[bool, str]`
3. Register in `OPERATOR_REGISTRY` dictionary
4. The condition evaluator will automatically discover and use it

### Database Model JSON Fields
Database models use explicit getter/setter methods for JSON fields instead of `@property` to avoid conflicts with SQLAlchemy's `metadata` attribute:
```python
# In api/database/models.py
def get_dimensions(self) -> list[Dict[str, Any]]:
    return json.loads(self.dimensions_json)

def set_dimensions(self, value: list[Dict[str, Any]]) -> None:
    self.dimensions_json = json.dumps(value)
```

When updating routers, always use these methods, not direct attribute access.

### Schema Validation
All items in a catalog must validate against their schema's dimensions. The Schema model's `validate_attributes()` method:
1. Checks required dimensions are present
2. Validates types match dimension definitions
3. Validates enum values are in allowed list
4. Validates numeric values are within min/max ranges
5. Validates list item types

### RuleEvaluation Passed Field
The `RuleEvaluation.passed` field indicates whether a rule allowed compatibility:

**For exclusion rules** (in `rulate/engine/evaluator.py:51-65`):
- Condition TRUE → exclusion applies → items incompatible → `passed=False`
- Condition FALSE → exclusion doesn't apply → `passed=True`
- Implementation: `passed = not result` (inverted from condition result)

**For requirement rules** (in `rulate/engine/evaluator.py:72-90`):
- Condition TRUE → requirement met → `passed=True`
- Condition FALSE → requirement not met → `passed=False`
- Implementation: `passed = result` (same as condition result)

This ensures that compatible items always show all rules as passed (4/4), and incompatible items show at least one failed rule.

### Example Configuration Structure
The `examples/wardrobe/` directory contains a complete working example:
- `schema.yaml` - 7 dimensions defining clothing attributes
- `rules.yaml` - 4 rules (2 exclusions, 2 requirements)
- `catalog.yaml` - 19 clothing items

This is the canonical reference for testing and demonstrating the system.

## Design Principles

1. **Generic First**: Core engine is domain-agnostic. Domain-specific logic lives in schemas and rules, not code.
2. **Declarative Configuration**: Rules and schemas are YAML/JSON, not Python code.
3. **Type Safety**: Pydantic models validate all data structures.
4. **Separation of Concerns**: Core engine, API persistence, and CLI are independent layers.
5. **Testable**: Pure functions in the evaluation engine, clear interfaces between layers.

## File Format Specifications

### Schema Files
```yaml
name: "schema_name"
version: "1.0.0"
dimensions:
  - name: "field_name"
    type: "enum|string|integer|float|boolean|list"
    required: true|false
    values: ["val1", "val2"]  # for enum
    min: 1                     # for integer/float
    max: 5                     # for integer/float
    item_type: "string"        # for list
```

### RuleSet Files
```yaml
name: "ruleset_name"
version: "1.0.0"
schema_ref: "schema_name"
rules:
  - name: "rule_name"
    type: "exclusion|requirement"
    enabled: true
    condition: {...}  # operator tree
```

### Catalog Files
```yaml
name: "catalog_name"
schema_ref: "schema_name"
items:
  - id: "item_id"
    name: "Item Name"
    attributes:
      field_name: value
```

## Current Status

- **Phase 1 (Complete)**: Core engine with 9 operators, comprehensive unit tests (480 tests, 94% coverage)
- **Phase 2 (Complete)**: REST API with SQLite, CLI tool with multiple output formats
  - **API Integration Tests (Complete)**: 217 integration tests achieving 88.5% API coverage
- **Phase 3 (Complete)**: SvelteKit web UI with interactive explorer and matrix visualization
- **Phases 4-7 (Complete)**: Comprehensive test suite across all layers (1,368 total tests)

### Backend Testing & Quality
- **Unit Tests**: 480 tests across 11 files with 94% core engine coverage
  - Schema validation, rule definitions, operators, evaluators, loaders, CLI
- **Integration Tests**: 217 tests across 7 files with 88.5% API coverage
  - All CRUD operations for 6 routers (schemas, rulesets, catalogs, items, evaluation, clusters, import/export)
  - Database isolation using environment variables with FastAPI TestClient
  - 5 of 6 routers at 100% coverage (import_export at 66%)
- **Test Infrastructure**: Function-scoped fixtures, in-memory SQLite, proper cleanup with engine.dispose()

### Frontend Testing & Quality
- **Test Suite**: 671 tests across 22 files with 100% pass rate
- **Coverage**: 100% on production code (API client, form utilities, core utilities)
- **API Client**: All 39 endpoints tested with 100% coverage
- **Form Utilities**: Pure TypeScript attribute handling with 37 tests for all dimension types
- **E2E Testing**: 72 tests across 3 browsers (Chromium, Firefox, WebKit) covering critical workflows
- **Test Infrastructure**: Cleaned up unused utilities, excluded test code from coverage metrics (standard practice)

### Recent Changes
- **API Integration Tests (December 2025)**: Comprehensive test coverage for REST API layer
  - 217 integration tests across 7 test files (88.5% API coverage)
  - All CRUD endpoints for schemas, rulesets, catalogs, items tested
  - Evaluation endpoints (pair, matrix, item) at 100% coverage
  - Cluster endpoints at 100% coverage
  - Import/export endpoints at 66% coverage
  - Test infrastructure with environment variable-based database isolation
- **UX Polish (December 2025)**: Comprehensive user experience improvements
  - Toast notifications replacing browser alerts (4 types, auto-dismiss, stacking)
  - Modal dialogs replacing browser confirms (accessible, focus trap, keyboard nav)
  - Enhanced RuleEditor with operator docs sidebar, search, and 18 templates
  - Loading states, empty states, tooltips, form validation utilities
  - Unsaved changes warnings
  - Zero browser `alert()` or `confirm()` calls remaining
- **Import/Export Functionality**: Comprehensive bulk data import/export capabilities
  - API endpoints for exporting/importing all data types with validation
  - Web UI page with file upload/download for backup and migration
  - Automatic dependency handling for imports
- **Web UI CRUD Operations**: Complete create/edit functionality for all entities
  - Schema creation form with dynamic dimension builder (all 6 types)
  - RuleSet and Catalog creation forms
  - Item creation/edit with schema-driven fields
  - Form validation and error handling
- **Interactive Features**: Explorer with item compatibility checking, matrix visualization, import/export workflows
- **Svelte 5 Compatibility**: Resolved SSR compilation issues, proper reactivity patterns

See `docs/SPECIFICATION.md` for complete technical specifications and `docs/roadmap/` for the enhancement roadmap.
