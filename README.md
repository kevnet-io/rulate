# Rulate

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
- **Extensible**: Easy to add custom rule types and operators

## Project Status

**Phase 1: Core Engine** ✅ COMPLETE

- [x] Project setup with dependencies (Pydantic, PyYAML, pytest)
- [x] Core models (Schema, Rule, Catalog, Evaluation)
- [x] Rule evaluation engine with operators
- [x] Example wardrobe configuration (19 items, 7 dimensions, 4 rules)
- [x] Comprehensive tests (44 tests, 95% coverage on schema)

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
- [x] CRUD interfaces for schemas, rulesets, and catalogs
- [x] Interactive compatibility explorer with clickable graph navigation
- [x] Compatibility matrix visualization with detailed rule evaluations
- [x] Responsive design with Tailwind CSS and accessible color palette
- [x] Real-time evaluation against REST API backend

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd rulate

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
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
uvicorn api.main:app --reload

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
uvicorn api.main:app --reload --port 8000

# Terminal 2: Start the web frontend
cd web
npm install  # First time only
npm run dev

# Web UI is now available at http://localhost:5173
```

The Web UI provides:
- **Dashboard**: Overview of schemas, rulesets, and catalogs
- **Explorer**: Interactive compatibility exploration - click through items to see what they're compatible/incompatible with
- **Matrix**: Visual grid showing all pairwise compatibility results
- **Management**: Create and view schemas, rulesets, catalogs, and items

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy rulate
```

## Documentation

See [SPECIFICATION.md](SPECIFICATION.md) for detailed technical specifications.

See [TASKS.md](TASKS.md) for development roadmap and task breakdown.

## License

TBD

## Contributing

This project is currently in early development.
