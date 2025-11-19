# Rulate

A generic, programmable rule-based comparison engine for evaluating and classifying relationships between pairs of objects.

## Overview

Rulate allows you to define schemas, rules, and catalogs to determine compatibility between objects. The initial use case is wardrobe compatibility checking (determining which clothing items can be worn together), but the engine is designed to be domain-agnostic.

## Features

- **Schema Definition**: Define dimensions and attributes for your domain
- **Declarative Rules**: Express compatibility logic in YAML/JSON
- **Type Safety**: Built with Pydantic for robust validation
- **CLI Interface**: Command-line tools for validation and evaluation
- **Extensible**: Easy to add custom rule types and operators

## Project Status

**Phase 1: Core Engine** ✅ COMPLETE

- [x] Project setup with dependencies (Pydantic, PyYAML, pytest)
- [x] Core models (Schema, Rule, Catalog, Evaluation)
- [x] Rule evaluation engine with operators
- [x] Example wardrobe configuration (19 items, 7 dimensions, 4 rules)
- [x] Comprehensive tests (44 tests, 95% coverage on schema)

**Phase 2: REST API** 🚧 Coming Next

- [ ] FastAPI backend with SQLite
- [ ] CRUD endpoints for schemas, rules, catalogs
- [ ] Import/export via API

**Phase 3: Web UI** 📅 Planned

- [ ] Svelte frontend
- [ ] Visual rule builder
- [ ] Compatibility matrix visualization

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
