# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rulate is a generic, programmable rule-based comparison engine for evaluating and classifying relationships between pairs of objects. The system uses declarative YAML/JSON schemas and rules to determine compatibility between items in a catalog.

**Initial use case**: Wardrobe compatibility checking (determining which clothing items can be worn together), but the engine is designed to be domain-agnostic.

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
- `rulate/engine/operators.py` - Operator implementations for rule conditions
- `rulate/engine/condition_evaluator.py` - Parses and evaluates condition dictionaries
- `rulate/engine/evaluator.py` - Main evaluation orchestrator (evaluate_pair, evaluate_matrix, evaluate_item_against_catalog)
- `rulate/utils/` - YAML/JSON loaders and exporters

### 2. REST API (`api/`)
FastAPI backend with SQLite persistence for managing schemas, rulesets, and catalogs via HTTP.

**Database architecture:**
- SQLAlchemy ORM with SQLite (`api/database/models.py`)
- Tables: `schemas`, `rulesets`, `catalogs`, `items`
- Complex fields (dimensions, rules, attributes) stored as JSON in TEXT columns
- Uses getter/setter methods (`get_dimensions()`, `set_dimensions()`) not properties to avoid SQLAlchemy metadata conflicts

**API structure:**
- `api/main.py` - FastAPI app setup with lifespan events
- `api/routers/` - Endpoint implementations (schemas, rulesets, catalogs, evaluation)
- `api/models/schemas.py` - Pydantic request/response models (distinct from core models)
- `api/database/connection.py` - Session management with `get_db()` dependency

**Important conversion pattern:**
The API routers convert between database models (SQLAlchemy) and core Rulate models (Pydantic) using helper functions like `db_to_rulate_schema()`, `db_to_rulate_catalog()` in `api/routers/evaluation.py`.

### 3. CLI Tool (`rulate/cli.py`)
Click-based command-line interface with three command groups:
- `validate` - Validate schema/rules/catalog files
- `evaluate` - Run compatibility evaluations (pair, matrix, item)
- `show` - Display information about schemas and catalogs

## Development Commands

### Setup
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_schema.py

# Run specific test
pytest tests/unit/test_schema.py::TestSchema::test_create_simple_schema

# Run with coverage
pytest --cov=rulate --cov-report=html
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

### Running the API
```bash
# Start server
uvicorn api.main:app --reload

# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
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
  --format summary  # or json, yaml, csv
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

- **Phase 1 (Complete)**: Core engine with 9 operators, comprehensive tests
- **Phase 2 (Complete)**: REST API with SQLite, CLI tool with multiple output formats
- **Phase 3 (Planned)**: Web UI with Svelte

See `SPECIFICATION.md` for detailed technical specifications and `TASKS.md` for development roadmap.
