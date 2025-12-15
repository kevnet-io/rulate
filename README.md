# Rulate

[![Tests](https://github.com/kevnet-io/rulate/actions/workflows/test.yml/badge.svg)](https://github.com/kevnet-io/rulate/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A generic, programmable rule-based comparison engine for evaluating and classifying relationships between pairs of objects.

## Overview

Rulate allows you to define schemas, rules, and catalogs to determine compatibility between objects. The initial use case is wardrobe compatibility checking (determining which clothing items can be worn together), but the engine is designed to be domain-agnostic.

## Features

- **Schema Definition**: Define dimensions and attributes for your domain
- **Declarative Rules**: Express compatibility logic in YAML/JSON
- **Type Safety**: Built with Pydantic for robust validation
- **REST API**: FastAPI backend with SQLite persistence
- **Web UI**: Interactive SvelteKit frontend for visual exploration
- **CLI Interface**: Command-line tools for validation and evaluation
- **Import/Export**: Bulk data import and export in JSON format for backup and migration
- **Extensible**: Easy to add custom rule types and operators

## Project Status

**Phase 1: Core Engine** ✅ COMPLETE

- [x] Project setup with dependencies (Pydantic, PyYAML, pytest)
- [x] Core models (Schema, Rule, Catalog, Evaluation)
- [x] Rule evaluation engine with operators
- [x] Example wardrobe configuration (19 items, 7 dimensions, 4 rules)
- [x] Comprehensive test coverage across all core modules

**Phase 2: REST API & CLI** ✅ COMPLETE

- [x] FastAPI backend with SQLite
- [x] CRUD endpoints for schemas, rulesets, catalogs, items
- [x] Evaluation endpoints (pair, matrix, item)
- [x] Request/response validation with Pydantic
- [x] Automatic OpenAPI documentation at `/docs`
- [x] CLI tool with validate, evaluate, and show commands
- [x] Multiple output formats (summary, json, yaml, csv, table)
- [x] Successfully tested with wardrobe example

**Phase 3: Web UI** ✅ COMPLETE

- [x] SvelteKit 2.0 frontend with TypeScript
- [x] Dashboard with overview statistics
- [x] Full CRUD operations for schemas, rulesets, catalogs, and items
  - [x] Create forms with validation and schema-driven dynamic fields
  - [x] Edit forms for updating items
  - [x] List and detail views with delete functionality
- [x] Interactive compatibility explorer with clickable graph navigation
- [x] Compatibility matrix visualization with detailed rule evaluations
- [x] Responsive design with Tailwind CSS and accessible color palette
- [x] Real-time evaluation against REST API backend
- [x] Professional UX with toast notifications, modals, loading states, and enhanced rule editor

**Phases 4-7: Testing & Data Management** ✅ COMPLETE

- [x] Comprehensive test suite (backend unit, frontend unit, E2E)
- [x] High test coverage across all layers
- [x] Import/export functionality for data backup and migration
- [x] Bulk operations via API and Web UI

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd rulate

# Install all dependencies (backend + frontend + pre-commit hooks)
make install

# Or use uv directly:
# uv sync --dev
```

## Quick Start

### Using the Python Library

```python
from rulate.utils import load_schema, load_ruleset, load_catalog
from rulate.engine import evaluate_pair, evaluate_matrix

# Load example wardrobe configuration
schema = load_schema('examples/wardrobe/schema.yaml')
ruleset = load_ruleset('examples/wardrobe/rules.yaml')
catalog = load_catalog('examples/wardrobe/catalog.yaml')

# Compare two items
shirt = catalog.get_item('shirt_001')
pants = catalog.get_item('pants_002')
result = evaluate_pair(shirt, pants, ruleset, schema)

print(f"Compatible: {result.compatible}")
print(result.get_summary())

# Generate full compatibility matrix
matrix = evaluate_matrix(catalog, ruleset, schema)
stats = matrix.get_summary_stats()
print(f"Compatibility rate: {stats['compatibility_rate']:.1%}")
```

### Using the CLI

```bash
# Validate files
rulate validate schema examples/wardrobe/schema.yaml
rulate validate catalog examples/wardrobe/catalog.yaml --schema examples/wardrobe/schema.yaml

# Evaluate compatibility
rulate evaluate pair shirt_001 pants_002 \
  --catalog examples/wardrobe/catalog.yaml \
  --rules examples/wardrobe/rules.yaml \
  --schema examples/wardrobe/schema.yaml

# Generate compatibility matrix
rulate evaluate matrix \
  --catalog examples/wardrobe/catalog.yaml \
  --rules examples/wardrobe/rules.yaml \
  --format summary

# Find compatible items for a specific item
rulate evaluate item shirt_001 \
  --catalog examples/wardrobe/catalog.yaml \
  --rules examples/wardrobe/rules.yaml

# Show catalog information
rulate show catalog examples/wardrobe/catalog.yaml

# Export matrix as CSV
rulate evaluate matrix \
  --catalog examples/wardrobe/catalog.yaml \
  --rules examples/wardrobe/rules.yaml \
  --format csv --output compatibility.csv
```

### Using the REST API

```bash
# Start the API server
make dev-backend

# Or use uvicorn directly:
# uvicorn api.main:app --reload

# API is now available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs

# Create a schema
curl -X POST http://localhost:8000/api/v1/schemas \
  -H "Content-Type: application/json" \
  -d @examples/wardrobe/schema.json

# Evaluate compatibility between two items
curl -X POST http://localhost:8000/api/v1/evaluate/pair \
  -H "Content-Type: application/json" \
  -d '{
    "item1_id": "shirt_001",
    "item2_id": "pants_001",
    "catalog_name": "my_wardrobe",
    "ruleset_name": "wardrobe_rules_v1"
  }'
```

### Using the Web UI

```bash
# Terminal 1: Start the API server
make dev-backend

# Terminal 2: Start the web frontend
make dev-frontend

# Web UI is now available at http://localhost:5173

# Or use the underlying commands:
# Terminal 1: uvicorn api.main:app --reload --port 8000
# Terminal 2: cd web && npm run dev
```

The Web UI provides:
- **Dashboard**: Overview of schemas, rulesets, and catalogs with statistics
- **Schema Management**: Create schemas with dynamic dimension builder supporting all 6 types (string, integer, float, boolean, enum, list)
- **RuleSet Management**: Create rulesets with enhanced rule editor featuring operator documentation, search, and 18 templates
- **Catalog Management**: Create catalogs and manage items with schema-driven forms
- **Item Editor**: Create and edit items with dynamic forms based on schema definitions
- **Explorer**: Interactive compatibility exploration - click through items to see what they're compatible/incompatible with
- **Matrix**: Visual grid showing all pairwise compatibility results with detailed rule evaluations
- **Import/Export**: Bulk import and export of all data types (schemas, rulesets, cluster rulesets, catalogs) with JSON file download and upload
- **UX Polish**: Toast notifications, accessible modals, loading states, empty states, form validation, and unsaved changes warnings

## Development

### Quick Reference

```bash
# Install dependencies
make install

# Start development servers
make dev-backend    # API server (http://localhost:8000)
make dev-frontend   # Web UI (http://localhost:5173)

# Run tests
make test           # Backend tests
make test-frontend  # Frontend unit tests
make test-e2e       # Frontend E2E tests (requires API running)

# Code quality
make format         # Auto-fix formatting issues
make check-all      # Verify all checks pass (run before pushing)

# See all available commands
make help
```

### Running Tests

```bash
# Backend tests
make test              # Run pytest suite
make test-cov          # With coverage report

# Frontend tests
make test-frontend     # Unit tests (vitest)
make test-e2e          # E2E tests (playwright)

# Or use underlying commands:
# uv run pytest
# uv run pytest --cov=rulate
# cd web && npm test
# cd web && npm run test:e2e
```

For detailed testing information, see [docs/SPECIFICATION.md](docs/SPECIFICATION.md#testing).

### Code Quality

Use the two-tier workflow for code quality:

```bash
# 1. During development - auto-fix issues (modifies files)
make format

# 2. Before pushing - verify all checks pass (read-only)
make check-all

# Individual quality checks (read-only)
make lint              # Ruff linting
make typecheck         # Mypy type checking
make lint-frontend     # ESLint

# Or use individual tools:
# uv run black .              # Format Python
# uv run ruff check .         # Lint Python
# uv run mypy rulate          # Type check core
# cd web && npm run lint      # Lint frontend
```

Pre-commit hooks run automatically on commit to enforce code quality.
Run `make help` to see all available commands.

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Development guide for contributors and Claude Code AI assistant
- **[docs/SPECIFICATION.md](docs/SPECIFICATION.md)** - Complete technical specification of the current implementation
- **[docs/roadmap/](docs/roadmap/)** - Enhancement roadmap organized by epic
- **[docs/UX_POLISH_SUMMARY.md](docs/UX_POLISH_SUMMARY.md)** - Comprehensive UX improvements and component documentation

## License

[MIT](./LICENSE)

## Contributing

Rulate is production-ready and welcomes contributions!

Please read our [Contributing Guide](CONTRIBUTING.md) for details on:
- Development setup and workflow
- Code style guidelines
- Testing requirements
- Pull request process
- How to report bugs and suggest features

See [docs/roadmap/](docs/roadmap/) for a prioritized list of enhancements we'd love help with!
