# Rulate - Rule-Based Comparison Engine

## Project Overview

Rulate is a generic, programmable rule-based comparison engine for evaluating and classifying relationships between pairs of objects. The initial use case is wardrobe compatibility checking (determining which clothing items can be worn together).

## Design Principles

1. **Generic First**: Core engine should be domain-agnostic
2. **Declarative Configuration**: Rules and schemas defined in YAML/JSON
3. **Type Safety**: Leverage Pydantic for validation
4. **Extensible**: Easy to add new rule types and evaluation logic
5. **Testable**: Pure functions, clear separation of concerns

---

## Core Concepts

### 1. Schema
Defines the **dimension space** for a domain - what attributes objects can have.

**Example (Wardrobe Domain):**
```yaml
schema:
  name: "wardrobe_v1"
  version: "1.0.0"
  dimensions:
    - name: "category"
      type: "enum"
      required: true
      values: ["shirt", "pants", "jacket", "shoes", "accessory"]

    - name: "body_zone"
      type: "enum"
      required: true
      values: ["head", "torso", "legs", "feet", "hands", "neck"]

    - name: "layer"
      type: "enum"
      required: false
      values: ["base", "mid", "outer"]

    - name: "formality"
      type: "integer"
      required: false
      min: 1
      max: 5

    - name: "colors"
      type: "list"
      item_type: "string"
      required: false

    - name: "season"
      type: "enum"
      required: false
      values: ["spring", "summer", "fall", "winter", "all_season"]
```

### 2. Rules
Defines **compatibility logic** - when two objects are compatible or incompatible.

**Rule Types:**

#### A. Exclusion Rules
Two items are **incompatible** if condition is met.

```yaml
rules:
  - name: "same_body_zone_exclusion"
    type: "exclusion"
    description: "Cannot wear two items on same body zone unless layering"
    condition:
      all:
        - equals:
            field: "body_zone"
        - not:
            has_different_layers: true
```

#### B. Requirement Rules
Two items are **only compatible** if condition is met.

```yaml
  - name: "formality_matching"
    type: "requirement"
    description: "Formality levels must be within 1 point"
    condition:
      abs_diff:
        field: "formality"
        max: 1
```

#### C. Custom Expression Rules
Advanced boolean logic.

```yaml
  - name: "color_harmony"
    type: "custom"
    expression: "colors_compatible(item1.colors, item2.colors)"
```

### 3. Catalog
Collection of **objects** with their attribute values.

```yaml
catalog:
  name: "my_wardrobe"
  schema_ref: "wardrobe_v1"
  items:
    - id: "shirt_001"
      name: "Blue Oxford Shirt"
      attributes:
        category: "shirt"
        body_zone: "torso"
        layer: "base"
        formality: 4
        colors: ["blue", "white"]
        season: "all_season"

    - id: "jeans_001"
      name: "Dark Denim Jeans"
      attributes:
        category: "pants"
        body_zone: "legs"
        formality: 2
        colors: ["blue", "black"]
        season: "all_season"
```

### 4. Evaluation Result
Output of pairwise comparison.

```json
{
  "item1_id": "shirt_001",
  "item2_id": "jeans_001",
  "compatible": true,
  "rules_evaluated": [
    {
      "rule_name": "same_body_zone_exclusion",
      "passed": true,
      "reason": "Different body zones (torso vs legs)"
    },
    {
      "rule_name": "formality_matching",
      "passed": true,
      "reason": "Formality difference: 2 (within threshold of 1)"
    }
  ],
  "metadata": {
    "evaluated_at": "2025-11-19T10:30:00Z"
  }
}
```

---

## System Architecture

```
┌─────────────────────────────────────────┐
│           Web UI (Phase 3)              │
│  - Catalog Manager                      │
│  - Rule Builder                         │
│  - Compatibility Matrix View            │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────┐
│       FastAPI Backend (Phase 2)         │
│  - CRUD Endpoints                       │
│  - Evaluation API                       │
│  - Import/Export                        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Core Engine (Phase 1)              │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Schema Validator                │   │
│  │ - Dimension definitions         │   │
│  │ - Type checking                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Rule Engine                     │   │
│  │ - Rule parser                   │   │
│  │ - Condition evaluator           │   │
│  │ - Boolean logic processor       │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Catalog Manager                 │   │
│  │ - Item CRUD                     │   │
│  │ - Validation against schema     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Evaluation Engine               │   │
│  │ - Pairwise comparison           │   │
│  │ - Rule application              │   │
│  │ - Result generation             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Data Models (Pydantic)

### Schema Models

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

    # For ENUM type
    values: Optional[List[str]] = None

    # For INTEGER/FLOAT
    min: Optional[float] = None
    max: Optional[float] = None

    # For LIST type
    item_type: Optional[str] = None

class Schema(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    dimensions: List[Dimension]

    def validate_item_attributes(self, attributes: Dict) -> bool:
        """Validate item attributes against schema"""
        pass
```

### Rule Models

```python
class RuleType(str, Enum):
    EXCLUSION = "exclusion"
    REQUIREMENT = "requirement"
    CUSTOM = "custom"

class Rule(BaseModel):
    name: str
    type: RuleType
    description: Optional[str] = None
    condition: Dict[str, Any]  # JSON representation of condition logic
    enabled: bool = True

class RuleSet(BaseModel):
    name: str
    version: str
    schema_ref: str  # References schema name
    rules: List[Rule]
```

### Catalog Models

```python
class Item(BaseModel):
    id: str
    name: str
    attributes: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}  # For tags, notes, etc.

    def get_attribute(self, key: str, default=None):
        return self.attributes.get(key, default)

class Catalog(BaseModel):
    name: str
    schema_ref: str
    items: List[Item]
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime
```

### Evaluation Models

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
    metadata: Dict[str, Any] = {}
    evaluated_at: datetime
```

---

## Rule Condition Language

### Operators

#### Field Comparisons
```yaml
# Equality check
equals:
  field: "body_zone"

# Not equals
not_equals:
  field: "category"
  value: "shoes"

# Numeric comparisons
greater_than:
  field: "formality"
  value: 3

less_than_or_equal:
  field: "formality"
  value: 2
```

#### Cross-Item Comparisons
```yaml
# Absolute difference
abs_diff:
  field: "formality"
  max: 1

# Check if values are different
has_different:
  field: "layer"
```

#### Logical Operators
```yaml
# AND
all:
  - equals:
      field: "body_zone"
  - not_equals:
      field: "layer"

# OR
any:
  - equals:
      field: "category"
      value: "accessory"
  - equals:
      field: "body_zone"
      value: "head"

# NOT
not:
  equals:
    field: "season"
    value: "summer"
```

#### List/Set Operations
```yaml
# Check if lists have intersection
has_intersection:
  field: "colors"

# Check if lists are disjoint
are_disjoint:
  field: "tags"
```

---

## Phase Breakdown

### Phase 1: Core Engine (Python Library)

**Deliverables:**
- Schema definition and validation
- Rule definition and parsing
- Evaluation engine (pairwise comparison)
- CLI for testing
- Unit tests
- Example wardrobe configuration

**Project Structure:**
```
rulate/
├── rulate/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── rule.py
│   │   ├── catalog.py
│   │   └── evaluation.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── schema_validator.py
│   │   ├── rule_parser.py
│   │   ├── condition_evaluator.py
│   │   └── evaluator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── loaders.py  # YAML/JSON loading
│   │   └── exporters.py
│   └── cli.py
├── examples/
│   └── wardrobe/
│       ├── schema.yaml
│       ├── rules.yaml
│       └── catalog.yaml
├── tests/
│   ├── test_schema.py
│   ├── test_rules.py
│   ├── test_evaluator.py
│   └── test_wardrobe.py
├── pyproject.toml
├── README.md
└── SPECIFICATION.md
```

### Phase 2: REST API

**Deliverables:**
- FastAPI application
- Database integration (SQLite)
- CRUD endpoints for schemas, rules, catalogs, items
- Evaluation endpoints
- Import/export endpoints
- API documentation (auto-generated)

**Endpoints:**
```
# Schemas
GET    /api/v1/schemas
POST   /api/v1/schemas
GET    /api/v1/schemas/{schema_name}
PUT    /api/v1/schemas/{schema_name}
DELETE /api/v1/schemas/{schema_name}

# Rules
GET    /api/v1/rulesets
POST   /api/v1/rulesets
GET    /api/v1/rulesets/{ruleset_name}
PUT    /api/v1/rulesets/{ruleset_name}
DELETE /api/v1/rulesets/{ruleset_name}

# Catalogs
GET    /api/v1/catalogs
POST   /api/v1/catalogs
GET    /api/v1/catalogs/{catalog_name}
PUT    /api/v1/catalogs/{catalog_name}
DELETE /api/v1/catalogs/{catalog_name}

# Items
GET    /api/v1/catalogs/{catalog_name}/items
POST   /api/v1/catalogs/{catalog_name}/items
GET    /api/v1/catalogs/{catalog_name}/items/{item_id}
PUT    /api/v1/catalogs/{catalog_name}/items/{item_id}
DELETE /api/v1/catalogs/{catalog_name}/items/{item_id}

# Evaluation
POST   /api/v1/evaluate/pair
POST   /api/v1/evaluate/matrix  # All pairwise comparisons
POST   /api/v1/evaluate/item/{item_id}  # Compare one item against all others

# Import/Export
POST   /api/v1/import/catalog
GET    /api/v1/export/catalog/{catalog_name}
POST   /api/v1/import/schema
GET    /api/v1/export/schema/{schema_name}
```

### Phase 3: Web UI

**Deliverables:**
- Svelte application
- Schema manager (view/edit dimensions)
- Rule builder (visual interface for creating rules)
- Catalog browser/editor
- Compatibility matrix visualization
- Import/export interface

**Key Screens:**
1. **Dashboard**: Overview of catalogs, schemas, rulesets
2. **Schema Editor**: Define/edit dimensions
3. **Rule Builder**: Visual rule creation with condition builder
4. **Catalog Manager**: Browse/edit items, add new items
5. **Compatibility Matrix**: Grid showing all pairwise comparisons
6. **Item Detail View**: See all compatible items for a selected item

---

## File Format Specifications

### Schema File (schema.yaml)
```yaml
name: "string"
version: "semver"
description: "string (optional)"
dimensions:
  - name: "string"
    type: "enum|string|integer|float|boolean|list"
    required: boolean
    description: "string (optional)"
    # Type-specific fields
    values: ["array", "of", "strings"]  # for enum
    min: number  # for integer/float
    max: number  # for integer/float
    item_type: "string"  # for list
```

### Rules File (rules.yaml)
```yaml
name: "string"
version: "semver"
schema_ref: "string"
rules:
  - name: "string"
    type: "exclusion|requirement|custom"
    description: "string (optional)"
    enabled: boolean
    condition:
      # Condition expression (see Rule Condition Language above)
```

### Catalog File (catalog.yaml)
```yaml
name: "string"
schema_ref: "string"
metadata:
  created_at: "ISO 8601 datetime"
  updated_at: "ISO 8601 datetime"
items:
  - id: "string"
    name: "string"
    attributes:
      dimension_name: value
    metadata:
      tags: ["array", "of", "strings"]
      notes: "string"
```

---

## Testing Strategy

### Unit Tests
- Schema validation logic
- Rule parsing and condition evaluation
- Individual operators (equals, abs_diff, etc.)
- Catalog item validation

### Integration Tests
- End-to-end evaluation with wardrobe example
- Rule combinations (multiple exclusions + requirements)
- Edge cases (missing optional fields, empty catalogs)

### Test Data
- Create comprehensive wardrobe example with:
  - 20-30 clothing items
  - 5-10 rules covering common scenarios
  - Known compatible/incompatible pairs for validation

---

## Future Enhancements (Post-MVP)

### Scoring System
Replace boolean compatibility with confidence scores (0-100%)

```python
class ScoredComparisonResult(BaseModel):
    item1_id: str
    item2_id: str
    compatibility_score: float  # 0.0 - 1.0
    rules_evaluated: List[ScoredRuleEvaluation]
```

### Multi-Item Validation
Validate outfits with 3+ items

```python
def evaluate_outfit(items: List[Item], rules: RuleSet) -> OutfitEvaluation:
    """Validate all pairwise combinations in the outfit"""
    pass
```

### Context/Occasion Support
Add context filtering

```yaml
context:
  occasion: "work"
  weather: "cold"

# Rules can reference context
- name: "weather_appropriate"
  type: "requirement"
  condition:
    context_match:
      field: "season"
      context_key: "weather"
```

### Performance Optimizations
- Cache evaluation results
- Batch processing for matrix evaluation
- Index commonly queried attributes

---

## Success Criteria

### Phase 1
- [ ] Schema validator correctly validates wardrobe catalog
- [ ] Rule engine evaluates all wardrobe rules correctly
- [ ] CLI can load example configs and run evaluations
- [ ] 90%+ test coverage

### Phase 2
- [ ] API successfully serves all CRUD operations
- [ ] Can import/export catalogs via API
- [ ] Database persists data correctly
- [ ] API documentation is complete

### Phase 3
- [ ] UI allows full catalog management
- [ ] Rule builder can create all rule types
- [ ] Compatibility matrix displays correctly
- [ ] Can import/export via UI

---

## Development Timeline (Estimates)

**Phase 1**: Core Engine
- Project setup & models: 1 session
- Schema validation: 1 session
- Rule parsing & condition evaluation: 2 sessions
- Evaluation engine: 1 session
- CLI & testing: 1 session

**Phase 2**: REST API
- FastAPI setup & database: 1 session
- CRUD endpoints: 2 sessions
- Evaluation endpoints: 1 session
- Testing: 1 session

**Phase 3**: Web UI
- Project setup & layout: 1 session
- Catalog manager: 2 sessions
- Rule builder: 2 sessions
- Compatibility matrix: 1 session
- Polish & testing: 1 session

**Total**: ~15 sessions
