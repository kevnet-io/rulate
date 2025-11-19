# Rulate - Task Breakdown

## Phase 1: Core Engine

### 1. Project Setup & Foundation
- [ ] **1.1** Initialize Python project structure
  - Create directory structure (`rulate/`, `tests/`, `examples/`)
  - Set up `pyproject.toml` with dependencies (pydantic, pyyaml, click for CLI)
  - Configure pytest

- [ ] **1.2** Create base Pydantic models
  - `models/schema.py`: DimensionType, Dimension, Schema
  - `models/rule.py`: RuleType, Rule, RuleSet
  - `models/catalog.py`: Item, Catalog
  - `models/evaluation.py`: RuleEvaluation, ComparisonResult

- [ ] **1.3** Add utility modules
  - `utils/loaders.py`: Load YAML/JSON files into models
  - `utils/exporters.py`: Export models to YAML/JSON

### 2. Schema Validation System
- [ ] **2.1** Implement Schema model with validation
  - Validate dimension definitions (enum must have values, etc.)
  - Ensure unique dimension names
  - Version validation (semver format)

- [ ] **2.2** Implement schema-based item validation
  - Check required dimensions are present
  - Validate dimension value types
  - Validate enum values against allowed values
  - Validate numeric ranges (min/max)
  - Validate list item types

- [ ] **2.3** Write tests for schema validation
  - Valid schema definitions
  - Invalid schemas (missing values, type mismatches)
  - Item validation against schema
  - Edge cases (optional fields, empty catalogs)

### 3. Rule Definition & Parsing
- [ ] **3.1** Define rule condition operators
  - Create operator registry/factory pattern
  - Implement field comparison operators:
    - `EqualsOperator`
    - `NotEqualsOperator`
    - `GreaterThanOperator`
    - `LessThanOperator`
    - `GreaterThanOrEqualOperator`
    - `LessThanOrEqualOperator`

- [ ] **3.2** Implement cross-item comparison operators
  - `FieldEqualsOperator` (both items have same value)
  - `AbsDiffOperator` (absolute difference in numeric fields)
  - `HasDifferentOperator` (values are different)

- [ ] **3.3** Implement logical operators
  - `AllOperator` (AND logic)
  - `AnyOperator` (OR logic)
  - `NotOperator` (negation)

- [ ] **3.4** Implement list/set operators
  - `HasIntersectionOperator` (lists share values)
  - `AreDisjointOperator` (lists have no common values)

- [ ] **3.5** Create rule parser
  - `engine/rule_parser.py`: Parse condition dictionaries into operator trees
  - Validate rule structure
  - Handle nested conditions

- [ ] **3.6** Write tests for rule parsing
  - Each operator type
  - Nested logical operators
  - Invalid rule structures

### 4. Condition Evaluation Engine
- [ ] **4.1** Implement condition evaluator
  - `engine/condition_evaluator.py`: Evaluate operator trees against item pairs
  - Return boolean result + explanation string

- [ ] **4.2** Implement operator base classes
  - Abstract `Operator` base class with `evaluate(item1, item2)` method
  - Concrete implementations for each operator type

- [ ] **4.3** Add evaluation context
  - Track evaluation path for debugging
  - Generate human-readable explanations
  - Handle missing fields gracefully

- [ ] **4.4** Write tests for condition evaluation
  - Single operator evaluations
  - Complex nested conditions
  - Missing field handling
  - Explanation generation

### 5. Pairwise Comparison Engine
- [ ] **5.1** Implement main evaluator
  - `engine/evaluator.py`: Main evaluation orchestrator
  - `evaluate_pair(item1, item2, ruleset, schema)` function
  - Apply exclusion rules (any fail → incompatible)
  - Apply requirement rules (all must pass → compatible)
  - Handle rule priorities/ordering

- [ ] **5.2** Implement result generation
  - Create ComparisonResult objects
  - Include all rule evaluations
  - Add metadata (timestamp, etc.)

- [ ] **5.3** Implement batch evaluation
  - `evaluate_matrix(catalog, ruleset, schema)` - all pairwise
  - `evaluate_item(item, catalog, ruleset, schema)` - one vs all
  - Optimization: skip symmetric pairs (A-B same as B-A)

- [ ] **5.4** Write tests for evaluation engine
  - Simple pairwise evaluation
  - Multiple rules (exclusions + requirements)
  - Matrix evaluation correctness
  - Edge cases (empty catalog, no rules)

### 6. CLI Interface
- [ ] **6.1** Create CLI application
  - `cli.py`: Click-based CLI
  - Commands:
    - `rulate validate schema <file>` - Validate schema file
    - `rulate validate catalog <file>` - Validate catalog against schema
    - `rulate validate rules <file>` - Validate ruleset file
    - `rulate evaluate pair <item1_id> <item2_id>` - Evaluate single pair
    - `rulate evaluate matrix` - Evaluate all pairs
    - `rulate evaluate item <item_id>` - Evaluate one item vs all

- [ ] **6.2** Add configuration loading
  - Config file to specify schema/rules/catalog paths
  - Environment variable support
  - Command-line argument overrides

- [ ] **6.3** Format output
  - Pretty-print evaluation results
  - Table format for matrix output
  - JSON output option for scripting

### 7. Example Configuration (Wardrobe)
- [ ] **7.1** Create wardrobe schema
  - `examples/wardrobe/schema.yaml`
  - Dimensions: category, body_zone, layer, formality, colors, season

- [ ] **7.2** Create wardrobe rules
  - `examples/wardrobe/rules.yaml`
  - Exclusion: same body_zone without different layers
  - Requirement: formality matching (within 1 point)
  - Custom: color harmony (simple version)

- [ ] **7.3** Create sample wardrobe catalog
  - `examples/wardrobe/catalog.yaml`
  - 20-30 diverse items covering:
    - Multiple categories (shirts, pants, jackets, shoes, accessories)
    - Various formality levels
    - Different seasons
    - Color variety

- [ ] **7.4** Create test cases from catalog
  - Document known compatible pairs
  - Document known incompatible pairs
  - Use as integration test fixtures

### 8. Documentation & Testing
- [ ] **8.1** Write README.md
  - Project overview
  - Installation instructions
  - Quick start guide
  - CLI usage examples

- [ ] **8.2** Create user guide
  - How to define a schema
  - How to write rules
  - How to create a catalog
  - Condition operator reference

- [ ] **8.3** Add inline documentation
  - Docstrings for all public APIs
  - Type hints throughout
  - Usage examples in docstrings

- [ ] **8.4** Achieve test coverage goals
  - Aim for 90%+ coverage
  - Integration tests with wardrobe example
  - Edge case coverage

### 9. Polish & Refinement
- [ ] **9.1** Error handling
  - Clear error messages for validation failures
  - Helpful hints for common mistakes
  - Proper exception hierarchy

- [ ] **9.2** Performance review
  - Profile matrix evaluation on 50+ item catalog
  - Optimize hot paths if needed
  - Consider caching strategy

- [ ] **9.3** Code quality
  - Linting (ruff/black)
  - Type checking (mypy)
  - Code review checklist

---

## Phase 2: REST API

### 1. FastAPI Setup
- [ ] **1.1** Initialize FastAPI project
  - Create `api/` directory structure
  - Set up FastAPI app with routers
  - Configure CORS, middleware

- [ ] **1.2** Database setup
  - SQLite database initialization
  - SQLAlchemy models (or Pydantic + raw SQL)
  - Alembic for migrations

- [ ] **1.3** Database schema design
  - Tables: schemas, rulesets, catalogs, items
  - Relationships and foreign keys
  - Indexes for common queries

### 2. CRUD Endpoints - Schemas
- [ ] **2.1** GET /api/v1/schemas
- [ ] **2.2** POST /api/v1/schemas
- [ ] **2.3** GET /api/v1/schemas/{schema_name}
- [ ] **2.4** PUT /api/v1/schemas/{schema_name}
- [ ] **2.5** DELETE /api/v1/schemas/{schema_name}

### 3. CRUD Endpoints - RuleSets
- [ ] **3.1** GET /api/v1/rulesets
- [ ] **3.2** POST /api/v1/rulesets
- [ ] **3.3** GET /api/v1/rulesets/{ruleset_name}
- [ ] **3.4** PUT /api/v1/rulesets/{ruleset_name}
- [ ] **3.5** DELETE /api/v1/rulesets/{ruleset_name}

### 4. CRUD Endpoints - Catalogs
- [ ] **4.1** GET /api/v1/catalogs
- [ ] **4.2** POST /api/v1/catalogs
- [ ] **4.3** GET /api/v1/catalogs/{catalog_name}
- [ ] **4.4** PUT /api/v1/catalogs/{catalog_name}
- [ ] **4.5** DELETE /api/v1/catalogs/{catalog_name}

### 5. CRUD Endpoints - Items
- [ ] **5.1** GET /api/v1/catalogs/{catalog_name}/items
- [ ] **5.2** POST /api/v1/catalogs/{catalog_name}/items
- [ ] **5.3** GET /api/v1/catalogs/{catalog_name}/items/{item_id}
- [ ] **5.4** PUT /api/v1/catalogs/{catalog_name}/items/{item_id}
- [ ] **5.5** DELETE /api/v1/catalogs/{catalog_name}/items/{item_id}

### 6. Evaluation Endpoints
- [ ] **6.1** POST /api/v1/evaluate/pair
  - Request: item1_id, item2_id, catalog_name, ruleset_name
  - Response: ComparisonResult

- [ ] **6.2** POST /api/v1/evaluate/matrix
  - Request: catalog_name, ruleset_name
  - Response: List of all pairwise comparisons

- [ ] **6.3** POST /api/v1/evaluate/item/{item_id}
  - Request: catalog_name, ruleset_name
  - Response: List of comparisons with all other items

### 7. Import/Export Endpoints
- [ ] **7.1** POST /api/v1/import/catalog
  - Accept YAML/JSON file upload
  - Validate and store in database

- [ ] **7.2** GET /api/v1/export/catalog/{catalog_name}
  - Export catalog as YAML/JSON

- [ ] **7.3** POST /api/v1/import/schema
- [ ] **7.4** GET /api/v1/export/schema/{schema_name}
- [ ] **7.5** POST /api/v1/import/ruleset
- [ ] **7.6** GET /api/v1/export/ruleset/{ruleset_name}

### 8. API Testing & Documentation
- [ ] **8.1** Write API tests
  - Test each endpoint
  - Test error cases
  - Test validation

- [ ] **8.2** Configure OpenAPI/Swagger docs
  - Add descriptions to endpoints
  - Add request/response examples
  - Tag organization

- [ ] **8.3** Integration tests
  - End-to-end workflows
  - Import → Evaluate → Export

### 9. Deployment Preparation
- [ ] **9.1** Add health check endpoint
- [ ] **9.2** Add logging
- [ ] **9.3** Docker configuration (optional)
- [ ] **9.4** Environment configuration

---

## Phase 3: Web UI

### 1. Svelte Project Setup
- [ ] **1.1** Initialize SvelteKit project
- [ ] **1.2** Set up routing
- [ ] **1.3** Configure API client
- [ ] **1.4** Set up styling (Tailwind/DaisyUI or similar)

### 2. Core Layout & Navigation
- [ ] **2.1** Create main layout component
- [ ] **2.2** Navigation sidebar/header
- [ ] **2.3** Routing structure

### 3. Dashboard
- [ ] **3.1** Overview page
  - List of catalogs
  - List of schemas
  - List of rulesets
  - Quick stats

### 4. Schema Manager
- [ ] **4.1** Schema list view
- [ ] **4.2** Schema detail view
- [ ] **4.3** Schema editor
  - Add/edit/remove dimensions
  - Dimension type selector
  - Validation rules

- [ ] **4.4** Import/export buttons

### 5. Rule Builder
- [ ] **5.1** RuleSet list view
- [ ] **5.2** RuleSet detail view
- [ ] **5.3** Visual rule builder
  - Condition builder UI
  - Operator selector
  - Field selector (based on schema)
  - Nested condition support

- [ ] **5.4** Rule testing interface
  - Select two items
  - Preview rule evaluation

### 6. Catalog Manager
- [ ] **6.1** Catalog list view
- [ ] **6.2** Catalog detail view
  - Item grid/list
  - Search/filter items

- [ ] **6.3** Item editor
  - Form based on schema dimensions
  - Dynamic field types
  - Validation feedback

- [ ] **6.4** Add/edit/delete items
- [ ] **6.5** Import/export catalog

### 7. Compatibility Matrix
- [ ] **7.1** Matrix visualization
  - Grid showing all items vs all items
  - Color coding (compatible/incompatible)
  - Hover for details

- [ ] **7.2** Item detail view
  - Show all compatible items for selected item
  - Show incompatible items with reasons

- [ ] **7.3** Filtering
  - Filter by category/attributes
  - Show only compatible/incompatible

### 8. Polish & UX
- [ ] **8.1** Loading states
- [ ] **8.2** Error handling
- [ ] **8.3** Confirmation dialogs
- [ ] **8.4** Toast notifications
- [ ] **8.5** Responsive design

### 9. Testing & Documentation
- [ ] **9.1** Component tests
- [ ] **9.2** E2E tests
- [ ] **9.3** User documentation
- [ ] **9.4** Deployment guide

---

## Development Workflow

### Getting Started (Now)
1. Complete Phase 1, Task 1: Project Setup
2. Build core models
3. Iterate on evaluation engine
4. Test with wardrobe example

### Session Structure
- Start each session by reviewing task list
- Pick 1-3 related tasks
- Implement, test, commit
- Update task list

### Definition of Done
Each task is complete when:
- [ ] Code is written
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] Code is committed to git

---

## Next Steps

Ready to start **Phase 1, Task 1.1: Project Setup**?

This will involve:
1. Creating the directory structure
2. Setting up `pyproject.toml`
3. Initializing git (already done)
4. Installing initial dependencies
