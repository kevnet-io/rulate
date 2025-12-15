# Rulate - Technical Specification

**Version**: 0.1.0
**Status**: Production-Ready
**Last Updated**: November 2025

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Concepts](#core-concepts)
4. [Data Models](#data-models)
5. [Operators Reference](#operators-reference)
6. [File Formats](#file-formats)
7. [API Reference](#api-reference)
8. [CLI Reference](#cli-reference)
9. [Web UI](#web-ui)
10. [Implementation Details](#implementation-details)

---

## Overview

Rulate is a generic, programmable rule-based comparison engine for evaluating and classifying relationships between pairs and sets of objects. While designed for wardrobe compatibility checking, the engine is completely domain-agnostic.

### Design Principles

1. **Generic First**: Core engine is domain-agnostic - domain logic lives in schemas and rules
2. **Declarative Configuration**: All rules and schemas defined in YAML/JSON
3. **Type Safety**: Built with Pydantic for robust validation
4. **Extensible**: Easy to add custom operators and evaluation logic
5. **Testable**: Pure functions with clear separation of concerns

### Key Features

- **Dual Evaluation Modes**: Pairwise compatibility and cluster finding
- **Two-Level Rule System**: Pairwise rules + cluster-level constraints
- **19 Built-in Operators**: 9 pairwise + 8 cluster + 2 logical base classes
- **REST API**: 42 endpoints with automatic OpenAPI documentation
- **Web UI**: 19 pages with interactive visualization
- **CLI**: Comprehensive command-line interface
- **Database Persistence**: SQLite with SQLAlchemy ORM
- **Import/Export**: Bulk data import/export for backup and migration
- **Comprehensive Testing**: 480 backend tests (94% coverage) + 671 frontend tests (100% production code coverage)

---

## Architecture

### Three-Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Web UI (SvelteKit 2.0)                    │
│  ┌────────────┬──────────────┬──────────────┬─────────────┐ │
│  │ Dashboard  │ Schema Mgmt  │ Catalog Mgmt │  Explorer   │ │
│  ├────────────┼──────────────┼──────────────┼─────────────┤ │
│  │ Matrix     │ Rule Builder │ Cluster View │  Item CRUD  │ │
│  └────────────┴──────────────┴──────────────┴─────────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP/REST (JSON)
┌───────────────────────────▼──────────────────────────────────┐
│                   REST API (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Routers: schemas, rulesets, catalogs, items,         │   │
│  │          evaluation, clusters, cluster-rulesets      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Database: SQLite + SQLAlchemy ORM                    │   │
│  │ Tables: SchemaDB, RuleSetDB, ClusterRuleSetDB,       │   │
│  │         CatalogDB, ItemDB                            │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬──────────────────────────────────┘
                            │ Direct Module Import
┌───────────────────────────▼──────────────────────────────────┐
│                    Core Engine (Python)                      │
│  ┌─────────────────┬──────────────────┬──────────────────┐  │
│  │ Schema          │ Pairwise         │ Cluster          │  │
│  │ Validator       │ Evaluator        │ Evaluator        │  │
│  │                 │                  │                  │  │
│  │ - 6 dimension   │ - 9 operators    │ - 8 operators    │  │
│  │   types         │ - Condition eval │ - Bron-Kerbosch  │  │
│  │ - Type checking │ - Result gen     │ - Graph building │  │
│  └─────────────────┴──────────────────┴──────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Models: Schema, RuleSet, ClusterRuleSet, Catalog,    │   │
│  │         Item, ComparisonResult, ClusterResult        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Utils: loaders.py, exporters.py                      │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  CLI (Click)    │
                   │ - validate      │
                   │ - evaluate      │
                   │ - show          │
                   └─────────────────┘
```

### Deployment Models

#### Development
Three separate processes for optimal developer experience:
- **Core Engine**: Python library (`rulate/`)
- **REST API**: FastAPI on port 8000 (`api/`)
- **Web UI**: Vite dev server on port 5173 (`web/`)

Development workflow:
```bash
# Terminal 1
make dev-backend  # API on port 8000

# Terminal 2
make dev-frontend  # Vite HMR on port 5173
```

#### Production
Single unified server for simplified deployment:
- **FastAPI serves both**:
  - API endpoints at `/api/v1/*`
  - Static frontend assets from `web/build/`
  - SPA routing with fallback to `index.html`
- **Single port**: 8000
- **No CORS needed**: Same-origin requests

Production deployment:
```bash
# Build frontend
cd web && npm run build

# Start unified server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Or use Makefile
make serve-production
```

The server serves:
- API endpoints at `/api/v1/*`
- Frontend assets from `web/build/`
- SPA routing for all non-API paths

### Directory Structure

```
rulate/
├── rulate/                    # Core engine
│   ├── models/               # Pydantic models
│   │   ├── schema.py        # Schema, Dimension, DimensionType
│   │   ├── rule.py          # Rule, RuleSet, RuleType
│   │   ├── catalog.py       # Item, Catalog
│   │   ├── evaluation.py    # ComparisonResult, RuleEvaluation
│   │   └── cluster.py       # ClusterRule, ClusterRuleSet, ClusterResult
│   ├── engine/              # Evaluation engines
│   │   ├── operators.py     # All 19 operator implementations
│   │   ├── condition_evaluator.py        # Pairwise condition parser
│   │   ├── cluster_condition_evaluator.py # Cluster condition parser
│   │   ├── evaluator.py     # Pairwise evaluation orchestrator
│   │   └── cluster_evaluator.py          # Cluster finding (Bron-Kerbosch)
│   ├── utils/               # Helper utilities
│   │   ├── loaders.py       # YAML/JSON → Pydantic models
│   │   └── exporters.py     # Pydantic models → YAML/JSON
│   └── cli.py               # Click CLI application
├── api/                      # REST API
│   ├── main.py              # FastAPI app
│   ├── database/
│   │   ├── models.py        # SQLAlchemy models
│   │   └── connection.py    # DB session management
│   ├── models/
│   │   └── schemas.py       # API request/response models
│   └── routers/             # API endpoints
│       ├── schemas.py       # Schema CRUD (5 endpoints)
│       ├── rulesets.py      # RuleSet CRUD (5 endpoints)
│       ├── catalogs.py      # Catalog + Item CRUD (9 endpoints)
│       ├── evaluation.py    # Pairwise evaluation (3 endpoints)
│       ├── clusters.py      # Cluster evaluation + CRUD (6 endpoints)
│       └── import_export.py # Bulk import/export (14 endpoints)
├── web/                      # SvelteKit Web UI
│   ├── src/
│   │   ├── routes/          # 19 pages
│   │   │   ├── +page.svelte              # Dashboard
│   │   │   ├── schemas/                  # Schema list/detail/create
│   │   │   ├── rulesets/                 # RuleSet list/detail/create
│   │   │   ├── catalogs/                 # Catalog list/detail/create
│   │   │   ├── catalogs/[name]/items/    # Item CRUD
│   │   │   ├── cluster-rulesets/         # ClusterRuleSet list/detail
│   │   │   ├── explore/                  # Interactive explorer
│   │   │   ├── matrix/                   # Compatibility matrix
│   │   │   ├── clusters/                 # Cluster visualization
│   │   │   └── import-export/            # Bulk import/export
│   │   └── lib/
│   │       ├── api/client.ts             # TypeScript API client
│   │       ├── stores/                   # Svelte 5 stores (toast, modal)
│   │       └── components/               # 19 UI components
├── tests/                    # Test suite
│   ├── unit/                # 11 test files with 480 tests
│   │   ├── test_schema.py
│   │   ├── test_rule.py
│   │   ├── test_catalog.py
│   │   ├── test_operators.py
│   │   ├── test_evaluator.py
│   │   ├── test_cluster_evaluator.py
│   │   ├── test_condition_evaluator.py
│   │   ├── test_evaluation.py
│   │   ├── test_loaders.py
│   │   ├── test_exporters.py
│   │   └── test_cli.py
│   ├── integration/         # Integration test infrastructure
│   └── conftest.py          # Shared test fixtures
├── examples/                 # Example configurations
│   └── wardrobe/
│       ├── schema.yaml      # 7 dimensions
│       ├── rules.yaml       # 4 pairwise rules
│       ├── cluster_rules.yaml # Cluster constraints
│       └── catalog.yaml     # 19 clothing items
├── docs/                     # Documentation
│   ├── CLAUDE.md            # Development guide
│   └── ORIGINAL_SPECIFICATION.md # Initial planning doc
├── README.md                 # User guide
├── SPECIFICATION.md          # This file
├── roadmap/                 # Enhancement roadmap (by epic)
└── pyproject.toml           # Package configuration
```

---

## Core Concepts

### 1. Schema

Defines the **dimension space** - the attributes that items can have.

**Supported Dimension Types:**
- `string` - Free-form text
- `integer` - Whole numbers with optional min/max
- `float` - Decimal numbers with optional min/max
- `boolean` - True/false values
- `enum` - Fixed set of allowed values
- `list` - Arrays with typed elements

**Example:**
```yaml
name: "wardrobe_v1"
version: "1.0.0"
dimensions:
  - name: "category"
    type: "enum"
    required: true
    values: ["shirt", "pants", "jacket", "shoes"]

  - name: "formality"
    type: "integer"
    required: false
    min: 1
    max: 5

  - name: "colors"
    type: "list"
    item_type: "string"
    required: false
```

### 2. Pairwise Rules

Defines compatibility between **two items**.

**Rule Types:**
- **Exclusion**: Items are incompatible if condition is TRUE
- **Requirement**: Items are compatible only if condition is TRUE

**Example:**
```yaml
name: "wardrobe_rules_v1"
version: "1.0.0"
schema_ref: "wardrobe_v1"
rules:
  - name: "same_body_zone_exclusion"
    type: "exclusion"
    enabled: true
    condition:
      all:
        - equals:
            field: "body_zone"
        - not:
            has_different:
              field: "layer"
```

### 3. Cluster Rules

Defines constraints for **sets of items** that form valid clusters.

**Two-Level System:**
1. **Pairwise RuleSet**: Determines which items CAN go together (builds compatibility graph)
2. **Cluster Rules**: Determines which sets FORM valid clusters (set-level constraints)

**Example:**
```yaml
name: "outfit_clusters_v1"
version: "1.0.0"
schema_ref: "wardrobe_v1"
pairwise_ruleset_ref: "wardrobe_rules_v1"
cluster_rules:
  - name: "minimum_outfit_size"
    enabled: true
    condition:
      min_cluster_size: 3

  - name: "unique_body_zones"
    enabled: true
    condition:
      unique_values:
        field: "body_zone"
```

### 4. Catalog

Collection of items with attributes validated against a schema.

**Example:**
```yaml
name: "my_wardrobe"
schema_ref: "wardrobe_v1"
items:
  - id: "shirt_001"
    name: "Blue Oxford Shirt"
    attributes:
      category: "shirt"
      body_zone: "torso"
      formality: 4
      colors: ["blue", "white"]
```

### 5. Evaluation Results

**Pairwise Comparison:**
```json
{
  "item1_id": "shirt_001",
  "item2_id": "pants_001",
  "compatible": true,
  "rules_evaluated": [
    {
      "rule_name": "same_body_zone_exclusion",
      "passed": true,
      "reason": "Different body_zone values: torso vs legs"
    }
  ],
  "evaluated_at": "2025-11-23T10:30:00Z"
}
```

**Cluster Results:**
```json
{
  "clusters": [
    {
      "items": ["shirt_001", "pants_001", "shoes_001"],
      "size": 3,
      "cluster_rules_evaluated": [
        {
          "rule_name": "minimum_outfit_size",
          "passed": true,
          "reason": "Cluster size 3 >= minimum 3"
        }
      ]
    }
  ],
  "relationships": [
    {
      "cluster1_index": 0,
      "cluster2_index": 1,
      "relationship": "subset"
    }
  ]
}
```

---

## Data Models

All models defined using Pydantic for validation and type safety.

### Schema Models

**`rulate/models/schema.py`**

```python
class DimensionType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST = "list"

class Dimension(BaseModel):
    name: str
    type: DimensionType
    required: bool = False
    description: Optional[str] = None
    values: Optional[List[str]] = None      # For ENUM
    min: Optional[float] = None             # For INTEGER/FLOAT
    max: Optional[float] = None             # For INTEGER/FLOAT
    item_type: Optional[str] = None         # For LIST

    def validate_value(self, value: Any) -> bool:
        """Validate a value against this dimension's constraints"""
        # Implementation handles type checking, range validation, enum validation

class Schema(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    dimensions: List[Dimension]

    def validate_attributes(self, attributes: Dict[str, Any]) -> None:
        """Validate item attributes against this schema"""
        # Raises ValidationError if invalid
```

### Rule Models

**`rulate/models/rule.py`**

```python
class RuleType(str, Enum):
    EXCLUSION = "exclusion"
    REQUIREMENT = "requirement"

class Rule(BaseModel):
    name: str
    type: RuleType
    description: Optional[str] = None
    condition: Dict[str, Any]  # Nested operator tree
    enabled: bool = True

class RuleSet(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    schema_ref: str
    rules: List[Rule]
```

### Cluster Models

**`rulate/models/cluster.py`**

```python
class ClusterRule(BaseModel):
    name: str
    description: Optional[str] = None
    condition: Dict[str, Any]  # Cluster operator tree
    enabled: bool = True

class ClusterRuleSet(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    schema_ref: str
    pairwise_ruleset_ref: str
    cluster_rules: List[ClusterRule]

class ClusterResult(BaseModel):
    items: List[str]  # Item IDs in this cluster
    size: int
    cluster_rules_evaluated: List[RuleEvaluation]
```

### Catalog Models

**`rulate/models/catalog.py`**

```python
class Item(BaseModel):
    id: str
    name: str
    attributes: Dict[str, Any]

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get attribute value with optional default"""

class Catalog(BaseModel):
    name: str
    schema_ref: str
    items: List[Item]

    def get_item(self, item_id: str) -> Optional[Item]:
        """Find item by ID"""
```

### Evaluation Models

**`rulate/models/evaluation.py`**

```python
class RuleEvaluation(BaseModel):
    rule_name: str
    passed: bool
    reason: str

class ComparisonResult(BaseModel):
    item1_id: str
    item2_id: str
    compatible: bool
    rules_evaluated: List[RuleEvaluation]
    evaluated_at: datetime

    def get_summary(self) -> str:
        """Generate human-readable summary"""

class MatrixResult(BaseModel):
    catalog_name: str
    ruleset_name: str
    comparisons: List[ComparisonResult]

    def get_summary_stats(self) -> Dict[str, Any]:
        """Calculate statistics (compatibility rate, etc.)"""
```

---

## Operators Reference

### Pairwise Operators (9 total)

Located in `rulate/engine/operators.py`

#### 1. EqualsOperator
Both items have the same value for a field.

```yaml
equals:
  field: "body_zone"
```

#### 2. HasDifferentOperator
Items have different values for a field.

```yaml
has_different:
  field: "layer"
```

#### 3. AbsDiffOperator
Absolute difference between numeric fields within threshold.

```yaml
abs_diff:
  field: "formality"
  max: 1
```

#### 4. AnyEqualsOperator
Either item has a specific value.

```yaml
any_equals:
  field: "category"
  value: "accessory"
```

#### 5. AnyMissingOperator
Either item is missing a field.

```yaml
any_missing:
  field: "season"
```

#### 6. AllOperator (Logical)
All nested conditions must be true (AND).

```yaml
all:
  - equals:
      field: "body_zone"
  - has_different:
      field: "color"
```

#### 7. AnyOperator (Logical)
Any nested condition must be true (OR).

```yaml
any:
  - equals:
      field: "category"
      value: "shirt"
  - equals:
      field: "category"
      value: "pants"
```

#### 8. NotOperator (Logical)
Negates nested condition.

```yaml
not:
  equals:
    field: "season"
    value: "summer"
```

#### 9. Operator (Base Class)
Abstract base for all pairwise operators.

```python
class Operator(ABC):
    @abstractmethod
    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        """Returns (result, explanation)"""
```

### Cluster Operators (8 total)

#### 1. MinClusterSizeOperator
Cluster must have at least N items.

```yaml
min_cluster_size: 3
```

#### 2. MaxClusterSizeOperator
Cluster must have at most N items.

```yaml
max_cluster_size: 5
```

#### 3. UniqueValuesOperator
All items must have different values for a field.

```yaml
unique_values:
  field: "body_zone"
```

#### 4. HasItemWithOperator
Cluster must contain item(s) matching criteria.

```yaml
has_item_with:
  field: "category"
  value: "shoes"
```

#### 5. CountByFieldOperator
Count distinct values for a field.

```yaml
count_by_field:
  field: "category"
  min: 2
  max: 4
```

#### 6. FormalityRangeOperator
Domain-specific: formality values within range.

```yaml
formality_range:
  max_diff: 1
```

#### 7. ClusterAllOperator (Logical)
All cluster conditions must be true.

```yaml
all:
  - min_cluster_size: 3
  - unique_values:
      field: "body_zone"
```

#### 8. ClusterAnyOperator (Logical)
Any cluster condition must be true.

```yaml
any:
  - min_cluster_size: 5
  - has_item_with:
      field: "category"
      value: "jacket"
```

#### 9. ClusterNotOperator (Logical)
Negates cluster condition.

```yaml
not:
  max_cluster_size: 2
```

---

## File Formats

### Schema File Format

**File**: `*.yaml` or `*.json`

```yaml
name: "schema_name"              # Required, unique identifier
version: "1.0.0"                 # Required, semver format
description: "Optional description"
dimensions:
  - name: "dimension_name"       # Required, alphanumeric + underscores
    type: "string"               # Required: string|integer|float|boolean|enum|list
    required: true               # Optional, default: false
    description: "Optional"

    # Type-specific fields:
    values: ["val1", "val2"]     # Required for enum
    min: 1                       # Optional for integer/float
    max: 10                      # Optional for integer/float
    item_type: "string"          # Required for list (string|integer|float|boolean)
```

### Pairwise RuleSet Format

```yaml
name: "ruleset_name"
version: "1.0.0"
schema_ref: "schema_name"        # Must reference existing schema
description: "Optional"
rules:
  - name: "rule_name"
    type: "exclusion"            # exclusion | requirement
    description: "Optional"
    enabled: true                # Optional, default: true
    condition:
      # Nested operator tree using pairwise operators
```

### Cluster RuleSet Format

```yaml
name: "cluster_ruleset_name"
version: "1.0.0"
schema_ref: "schema_name"
pairwise_ruleset_ref: "ruleset_name"  # References pairwise rules
description: "Optional"
cluster_rules:
  - name: "cluster_rule_name"
    description: "Optional"
    enabled: true
    condition:
      # Nested operator tree using cluster operators
```

### Catalog Format

```yaml
name: "catalog_name"
schema_ref: "schema_name"
items:
  - id: "unique_item_id"         # Required, unique within catalog
    name: "Display Name"         # Required
    attributes:
      dimension_name: value      # Must match schema
```

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive Documentation: `http://localhost:8000/docs`

### Schemas (5 endpoints)

```
POST   /schemas
GET    /schemas
GET    /schemas/{schema_name}
PUT    /schemas/{schema_name}
DELETE /schemas/{schema_name}
```

### RuleSets (5 endpoints)

```
POST   /rulesets
GET    /rulesets
GET    /rulesets/{ruleset_name}
PUT    /rulesets/{ruleset_name}
DELETE /rulesets/{ruleset_name}
```

### Catalogs (4 endpoints)

```
POST   /catalogs
GET    /catalogs
GET    /catalogs/{catalog_name}
DELETE /catalogs/{catalog_name}
```

### Items (5 endpoints)

```
POST   /catalogs/{catalog_name}/items
GET    /catalogs/{catalog_name}/items
GET    /catalogs/{catalog_name}/items/{item_id}
PUT    /catalogs/{catalog_name}/items/{item_id}
DELETE /catalogs/{catalog_name}/items/{item_id}
```

### Evaluation (3 endpoints)

```
POST   /evaluate/pair
  Body: {
    "item1_id": "string",
    "item2_id": "string",
    "catalog_name": "string",
    "ruleset_name": "string"
  }

POST   /evaluate/matrix
  Body: {
    "catalog_name": "string",
    "ruleset_name": "string"
  }

POST   /evaluate/item
  Body: {
    "item_id": "string",
    "catalog_name": "string",
    "ruleset_name": "string"
  }
```

### Cluster RuleSets (5 endpoints)

```
POST   /cluster-rulesets
GET    /cluster-rulesets
GET    /cluster-rulesets/{cluster_ruleset_name}
PUT    /cluster-rulesets/{cluster_ruleset_name}
DELETE /cluster-rulesets/{cluster_ruleset_name}
```

### Clusters (1 endpoint)

```
POST   /evaluate/clusters
  Body: {
    "catalog_name": "string",
    "cluster_ruleset_name": "string"
  }
```

### Import/Export (14 endpoints)

**Export Endpoints (9):**
```
GET    /export/schemas
GET    /export/schemas/{schema_name}
GET    /export/rulesets
GET    /export/rulesets/{ruleset_name}
GET    /export/cluster-rulesets
GET    /export/cluster-rulesets/{cluster_ruleset_name}
GET    /export/catalogs
GET    /export/catalogs/{catalog_name}
GET    /export/all
```

**Import Endpoints (5):**
```
POST   /import/schemas
  Body: {"schemas": [...]}

POST   /import/rulesets
  Body: {"rulesets": [...]}

POST   /import/cluster-rulesets
  Body: {"cluster_rulesets": [...]}

POST   /import/catalogs
  Body: {"catalogs": [...]}

POST   /import/all
  Body: {
    "schemas": [...],
    "rulesets": [...],
    "cluster_rulesets": [...],
    "catalogs": [...]
  }
```

---

## CLI Reference

Main command: `rulate`

### Validate Commands

```bash
# Validate schema file
rulate validate schema <file>

# Validate ruleset file
rulate validate rules <file> [--schema <schema_file>]

# Validate catalog against schema
rulate validate catalog <file> --schema <schema_file>
```

### Evaluate Commands

```bash
# Evaluate single pair
rulate evaluate pair <item1_id> <item2_id> \
  --catalog <file> \
  --rules <file> \
  [--schema <file>]

# Generate compatibility matrix
rulate evaluate matrix \
  --catalog <file> \
  --rules <file> \
  [--format summary|json|yaml|csv|table] \
  [--output <file>]

# Evaluate one item against all others
rulate evaluate item <item_id> \
  --catalog <file> \
  --rules <file> \
  [--format summary|json]

# Find clusters
rulate evaluate clusters \
  --catalog <file> \
  --cluster-rules <file> \
  [--format summary|json]
```

### Show Commands

```bash
# Display schema information
rulate show schema <file>

# Display catalog information
rulate show catalog <file>
```

---

## Web UI

**URL**: `http://localhost:5173` (dev server)

### Pages (19 total)

#### Management Pages
- `/` - Dashboard with overview statistics
- `/schemas` - Schema list
- `/schemas/{name}` - Schema detail
- `/schemas/new` - Create schema
- `/rulesets` - RuleSet list
- `/rulesets/{name}` - RuleSet detail
- `/rulesets/new` - Create ruleset
- `/catalogs` - Catalog list
- `/catalogs/{name}` - Catalog detail
- `/catalogs/new` - Create catalog

#### Item Management
- `/catalogs/{name}/items/new` - Create item
- `/catalogs/{name}/items/{id}` - Item detail
- `/catalogs/{name}/items/{id}/edit` - Edit item

#### Visualization
- `/explore` - Interactive compatibility explorer
- `/matrix` - Compatibility matrix grid

#### Cluster Features
- `/cluster-rulesets` - ClusterRuleSet list
- `/cluster-rulesets/{name}` - ClusterRuleSet detail
- `/clusters` - Cluster visualization

#### Data Management
- `/import-export` - Bulk import/export for backup and migration

### Key Features

- **Dynamic Forms**: Schema-driven form generation for items
- **Live Validation**: Real-time validation feedback
- **Interactive Navigation**: Click-through exploration
- **Color-Coded Results**: Emerald (compatible) / Rose (incompatible)
- **TypeScript Client**: Fully typed API integration
- **Responsive Design**: Mobile-friendly Tailwind CSS

---

## Implementation Details

### Evaluation Algorithm

**Pairwise Evaluation** (`rulate/engine/evaluator.py`):

1. Load schema, ruleset, catalog
2. Validate items against schema
3. For each item pair:
   - Apply all exclusion rules
     - If any condition is TRUE → incompatible (passed=False)
   - Apply all requirement rules
     - If any condition is FALSE → incompatible (passed=False)
   - All rules passed → compatible
4. Return ComparisonResult

**Important**: For exclusion rules, `RuleEvaluation.passed = not condition_result`

**Cluster Finding** (`rulate/engine/cluster_evaluator.py`):

1. Build compatibility graph using pairwise ruleset
2. Find all maximal cliques using Bron-Kerbosch algorithm
3. For each clique:
   - Apply all cluster rules
   - If all pass → valid cluster
4. Detect relationships (subset, superset, overlapping)
5. Return ClusterResult

### Database Schema

**SQLAlchemy Models** (`api/database/models.py`):

- `SchemaDB` - Stores dimensions as JSON
- `RuleSetDB` - Stores rules as JSON, foreign key to SchemaDB
- `ClusterRuleSetDB` - Foreign keys to SchemaDB and RuleSetDB
- `CatalogDB` - Foreign key to SchemaDB
- `ItemDB` - Stores attributes as JSON, foreign key to CatalogDB

**Important**: Database models use getter/setter methods (not properties) for JSON fields to avoid SQLAlchemy metadata conflicts.

### Testing

**Backend Testing** (`tests/`):
- **480 tests** across 11 test files with **94% overall code coverage**
- **Test Files**:
  - `test_schema.py` - Schema validation and dimension types
  - `test_rule.py` - Rule definitions and validation
  - `test_catalog.py` - Catalog and item models
  - `test_operators.py` - All 19 operators (pairwise and cluster)
  - `test_evaluator.py` - Pairwise evaluation logic
  - `test_cluster_evaluator.py` - Cluster finding algorithm (Bron-Kerbosch)
  - `test_condition_evaluator.py` - Condition parsing and evaluation
  - `test_evaluation.py` - Evaluation result models
  - `test_loaders.py` - YAML/JSON loading
  - `test_exporters.py` - YAML/JSON exporting
  - `test_cli.py` - CLI commands and output formats
- **Coverage by Module**:
  - Core models: 98-100% coverage
  - Engine (operators, evaluators): 91-98% coverage
  - Utils (loaders, exporters): 90-100% coverage
  - CLI: 91% coverage

**Frontend Testing** (`web/src/`):
- **671 tests** across 22 test files with **100% production code coverage**
- **Unit Tests**:
  - API client: All 42 endpoints tested (100% coverage)
  - Form utilities: 37 tests for all 6 dimension types
  - UI components: Badge, Button, Card, Skeleton, Navigation
  - Page components: All 19 pages tested
- **E2E Tests** (`web/e2e/`):
  - 72 tests across 3 browsers (Chromium, Firefox, WebKit)
  - Schema management workflow
  - Catalog and item CRUD operations
  - Interactive compatibility explorer
  - Navigation and routing
- **Test Infrastructure**:
  - Vitest 4.0 for unit tests
  - Playwright for E2E testing
  - happy-dom environment for Svelte 5
  - Coverage reports with @vitest/coverage-v8

**Test Data**:
- `examples/wardrobe/`: Complete working example
  - 7 dimensions
  - 4 pairwise rules
  - Cluster rules
  - 19 clothing items

**Running Tests**:
```bash
# Backend tests
uv run pytest                    # Run all tests
uv run pytest --cov=rulate       # With coverage report

# Frontend tests
cd web
npm test                         # Run unit tests
npm run test:coverage            # With coverage report
npm run test:e2e                 # Run E2E tests
npm run test:e2e:ui              # E2E tests with UI
```

### Performance Considerations

- **Matrix evaluation**: Skips symmetric pairs (A-B same as B-A)
- **Cluster finding**: Efficient Bron-Kerbosch with pivoting
- **Database**: JSON fields for flexibility vs. normalized tables

---

## Project Metrics

- **Python Files**: 30+ files
- **Lines of Code**: ~10,000+ lines
- **Operators**: 19 total (9 pairwise + 8 cluster + 2 base)
- **API Endpoints**: 42 endpoints across 6 routers
- **Web UI Pages**: 19 pages
- **UI Components**: 19 reusable components (includes 10 UX polish components)
- **Backend Tests**: 480 tests (94% coverage)
- **Frontend Tests**: 671 tests (100% production code coverage)
- **Total Test Count**: 1,151 tests
- **Dependencies**: Pydantic, FastAPI, SQLAlchemy, Click, SvelteKit, Vitest, Playwright

---

## Version History

**v0.1.0** (November-December 2025)
- Initial production-ready release
- Complete pairwise and cluster evaluation
- Full-stack implementation (Core + API + Web UI)
- 42 API endpoints with import/export
- 19 Web UI pages including data management
- 19 operators (9 pairwise + 8 cluster + 2 base)
- Comprehensive wardrobe example
- 1,151 total tests with high coverage (94% backend, 100% frontend production code)

---

## See Also

- `README.md` - User guide and quick start
- `docs/CLAUDE.md` - Development guide for contributors
- `docs/UX_POLISH_SUMMARY.md` - Comprehensive UX improvements documentation
- `docs/ORIGINAL_SPECIFICATION.md` - Initial planning document
- `docs/roadmap/` - Enhancement roadmap organized by epic
- `/docs` - Interactive API documentation (when server running)
