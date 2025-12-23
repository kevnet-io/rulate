# Coverage-Layer Conflict Pattern

## Overview

The **coverage-layer conflict pattern** is a reusable approach for modeling compatibility between items that occupy overlapping spatial or logical zones with varying degrees of precedence. This pattern was developed for the gender-agnostic wardrobe domain but can be applied to any domain requiring granular conflict detection across multiple dimensions.

## Core Concept

Items specify coverage across multiple zones (parts) with associated layer values indicating precedence or hierarchy:

```yaml
item:
  coverage_layers:
    - parts: [zone_a, zone_b]
      layer: 2.0
    - parts: [zone_c, zone_d]
      layer: 1.5
```

**Key Innovation**: Different zones within a single item can have different layer values, enabling complex compatibility modeling.

## Conflict Detection Algorithm

The `PartLayerConflictOperator` detects two types of conflicts:

### 1. Same-Layer Collision

When two items cover the same zone at the same layer value, they physically cannot coexist.

```yaml
# Item A
coverage_layers:
  - parts: [zone_1]
    layer: 2.0

# Item B
coverage_layers:
  - parts: [zone_1]
    layer: 2.0

# Result: CONFLICT (collision on zone_1)
```

### 2. Phasing Violation

When two items have inconsistent layer relationships across different overlapping zones, creating a physical impossibility.

**Example of phasing violation:**

```yaml
# Item A
coverage_layers:
  - parts: [chest]
    layer: 2.0  # A over B on chest
  - parts: [legs]
    layer: 1.0  # A under B on legs

# Item B
coverage_layers:
  - parts: [chest]
    layer: 1.0  # B under A on chest
  - parts: [legs]
    layer: 2.0  # B over A on legs

# Result: CONFLICT (phasing violation)
# A cannot be simultaneously over AND under B
```

**Phasing detection ensures consistent ordering**: If item A is "over" item B on any overlapping zone, A must be over (or equal to) B on ALL overlapping zones.

## Wardrobe Domain Example

### Schema Definition

```yaml
name: "wardrobe_v2"
version: "2.0.0"
dimensions:
  - name: "coverage_layers"
    type: "part_layer_list"
    required: true
    part_vocabulary:
      - "chest"
      - "upper_back"
      - "lower_back"
      - "waist"
      - "hips"
      - "upper_leg"
      - "lower_leg"
      - "feet"
      # ... 22 total body parts
```

### Rule Definition

```yaml
name: "wardrobe_rules_v2"
version: "2.0.0"
rules:
  - name: "coverage_layer_conflict"
    type: "exclusion"
    description: "Items cannot have conflicting coverage-layer relationships"
    condition:
      part_layer_conflict:
        field: "coverage_layers"
```

### Catalog Items

```yaml
# Undershirt - layer 1.0 base layer
- id: "undershirt_001"
  name: "Tank Undershirt"
  attributes:
    coverage_layers:
      - parts: [chest, upper_back, lower_back]
        layer: 1.0

# Dress shirt - layer 2.0 middle layer
- id: "shirt_001"
  name: "White Oxford Shirt"
  attributes:
    coverage_layers:
      - parts: [shoulders, chest, upper_back, lower_back, upper_arm]
        layer: 2.0

# Sweater - layer 3.0 outer layer
- id: "sweater_001"
  name: "Crew Neck Sweater"
  attributes:
    coverage_layers:
      - parts: [shoulders, chest, upper_back, lower_back, upper_arm, lower_arm]
        layer: 3.0

# Bodycon dress - mixed layers (tight top, flowy bottom)
- id: "dress_001"
  name: "Bodycon Dress"
  attributes:
    coverage_layers:
      - parts: [shoulders, chest, waist, upper_back, lower_back]
        layer: 2.0  # Tight bodice
      - parts: [hips, upper_leg]
        layer: 1.5  # Flowy skirt (lower layer)
```

### Compatibility Results

```
✅ undershirt + shirt = COMPATIBLE (1.0 < 2.0 on chest)
✅ shirt + sweater = COMPATIBLE (2.0 < 3.0 on chest)
✅ undershirt + sweater = COMPATIBLE (1.0 < 3.0 on chest)
✅ dress + tights = COMPATIBLE (1.5 > 1.0 on legs)
✅ dress + bra = COMPATIBLE (2.0 > 0.5 on chest)
❌ shirt + sweater (same category) = INCOMPATIBLE (different rule)
❌ two pants = INCOMPATIBLE (2.0 == 2.0 on legs - collision)
```

## Other Domain Applications

### 1. Furniture Placement

**Use Case**: Room layout planning with furniture occupying floor space at different heights.

```yaml
# Schema
dimensions:
  - name: "space_layers"
    type: "part_layer_list"
    part_vocabulary:
      - "floor_area_1"
      - "floor_area_2"
      - "wall_north"
      - "wall_south"
      # ... room zones

# Items
- id: "coffee_table"
  space_layers:
    - parts: [floor_area_1]
      layer: 1.0  # Low height

- id: "area_rug"
  space_layers:
    - parts: [floor_area_1, floor_area_2]
      layer: 0.5  # On floor, under furniture

- id: "sofa"
  space_layers:
    - parts: [floor_area_2, wall_south]
      layer: 2.0  # Against wall

# Rule
- name: "space_conflict"
  type: "exclusion"
  condition:
    part_layer_conflict:
      field: "space_layers"
```

**Results**:
- ✅ Area rug (0.5) + Coffee table (1.0) = Compatible (rug under table)
- ❌ Two sofas at same floor area = Conflict (both layer 2.0)

### 2. Equipment Mounting

**Use Case**: Laboratory or workshop equipment with mounting points and power zones.

```yaml
# Schema
dimensions:
  - name: "mount_layers"
    type: "part_layer_list"
    part_vocabulary:
      - "bench_left"
      - "bench_center"
      - "bench_right"
      - "overhead_rail"
      - "power_circuit_a"
      - "power_circuit_b"

# Items
- id: "microscope_001"
  mount_layers:
    - parts: [bench_center]
      layer: 2.0  # Primary equipment
    - parts: [power_circuit_a]
      layer: 1.0  # Power requirement

- id: "lamp_001"
  mount_layers:
    - parts: [overhead_rail]
      layer: 3.0  # Overhead
    - parts: [power_circuit_a]
      layer: 1.0  # Shared power OK

- id: "centrifuge_001"
  mount_layers:
    - parts: [bench_center]
      layer: 2.0  # Primary equipment
    - parts: [power_circuit_b]
      layer: 1.0  # Different circuit

# Rule
- name: "mounting_conflict"
  type: "exclusion"
  condition:
    part_layer_conflict:
      field: "mount_layers"
```

**Results**:
- ✅ Microscope + Lamp = Compatible (different bench zones, shared power OK)
- ❌ Microscope + Centrifuge = Conflict (both on bench_center at layer 2.0)

### 3. Network Architecture

**Use Case**: Service deployment with port bindings and resource allocation.

```yaml
# Schema
dimensions:
  - name: "resource_layers"
    type: "part_layer_list"
    part_vocabulary:
      - "port_80"
      - "port_443"
      - "port_8080"
      - "cpu_pool"
      - "memory_pool"
      - "disk_io"

# Items
- id: "nginx_reverse_proxy"
  resource_layers:
    - parts: [port_80, port_443]
      layer: 1.0  # Front-facing
    - parts: [cpu_pool, memory_pool]
      layer: 0.5  # Light resource usage

- id: "web_app_backend"
  resource_layers:
    - parts: [port_8080]
      layer: 1.0  # Backend port
    - parts: [cpu_pool, memory_pool]
      layer: 0.5  # Shared resources OK

- id: "database"
  resource_layers:
    - parts: [cpu_pool, disk_io]
      layer: 2.0  # Heavy resource usage
    - parts: [memory_pool]
      layer: 0.5  # Shared memory OK

# Rule
- name: "resource_conflict"
  type: "exclusion"
  condition:
    part_layer_conflict:
      field: "resource_layers"
```

**Results**:
- ✅ Nginx + Web App = Compatible (different ports, shared resources OK)
- ❌ Two services on port_80 = Conflict (collision)

## Implementation Requirements

### 1. Dimension Type: `part_layer_list`

Add to `rulate/models/schema.py`:

```python
class DimensionType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST = "list"
    PART_LAYER_LIST = "part_layer_list"  # Add this
```

### 2. Schema Dimension Definition

```python
class Dimension(BaseModel):
    name: str
    type: DimensionType
    required: bool = False
    part_vocabulary: list[str] | None = None  # For part_layer_list
    # ... other fields
```

### 3. Value Validation

Validation rules for `part_layer_list`:
- Outer: Must be list
- Each item: Must be dict with `parts` and `layer` keys
- `parts`: List of strings (validated against vocabulary if provided)
- `layer`: Numeric value >= 0

### 4. Operator Implementation

Key algorithm for phasing detection:

```python
class PartLayerConflictOperator(Operator):
    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
        # Build part → layer mappings
        part_to_layer1 = {part: layer for tuple in tuples1 for part in tuple["parts"]}
        part_to_layer2 = {part: layer for tuple in tuples2 for part in tuple["parts"]}

        # Find overlapping parts
        overlapping_parts = set(part_to_layer1.keys()) & set(part_to_layer2.keys())

        # Track consistent ordering
        item1_over_item2 = None

        for part in overlapping_parts:
            layer1 = part_to_layer1[part]
            layer2 = part_to_layer2[part]

            # Same layer = collision
            if layer1 == layer2:
                return True, f"Conflict: {part} at same layer {layer1}"

            # Check ordering consistency
            current_relationship = "over" if layer1 > layer2 else "under"

            if item1_over_item2 is None:
                item1_over_item2 = current_relationship
            elif item1_over_item2 != current_relationship:
                # Phasing violation detected
                return True, f"Phasing violation on {part}"

        return False, "No conflicts"
```

## Design Decisions

### Optional Part Vocabulary

The `part_vocabulary` field is **optional** to provide flexibility:

**With vocabulary** (strict validation):
```yaml
part_vocabulary: ["chest", "legs", "arms"]
# Only these parts allowed → validation errors for typos
```

**Without vocabulary** (flexible):
```yaml
part_vocabulary: null
# Any string allowed → enables dynamic domains
```

**Recommendation**: Use vocabulary for fixed domains (wardrobe, furniture), omit for dynamic domains (user-defined zones).

### Layer Value Types

Both `int` and `float` are supported for layer values:

```yaml
# Integer layers (simpler)
layer: 1  # Base
layer: 2  # Middle
layer: 3  # Outer

# Float layers (granular)
layer: 1.0  # Base
layer: 1.5  # Between base and middle
layer: 2.0  # Middle
layer: 2.5  # Between middle and outer
```

**Recommendation**: Use floats for domains requiring fine-grained layering (e.g., wardrobe with complex garments).

### Missing Field Handling

When `coverage_layers` field is missing from an item:

```python
if tuples1 is None or tuples2 is None:
    return False, "One or both items missing 'coverage_layers' (no conflict)"
```

**Design choice**: Graceful degradation - missing field means "no coverage" → no conflicts. This allows partial adoption in catalogs.

## Testing Strategy

### Unit Tests (12 tests)

1. No overlap → no conflict
2. Different layers on same parts → no conflict
3. Same layer on same part → conflict
4. **Phasing violation → conflict** (critical)
5. Missing field handling
6. Invalid configuration
7. Partial overlaps
8. Multiple tuples per item
9. Registry verification
10. Empty coverage list
11. Single part overlap
12. Complex multi-part scenarios

### Integration Tests

End-to-end test with schema, catalog, and ruleset:
- Load schema with `part_layer_list` dimension
- Load catalog with diverse items
- Load ruleset with `part_layer_conflict` rule
- Test known compatible pairs (undershirt + shirt)
- Test known incompatible pairs (two shirts)
- Test phasing violations (hybrid garments)

## Benefits of This Pattern

1. **Single Schema**: No need for separate masculine/feminine schemas
2. **Granular Modeling**: Different zones can have different precedence within a single item
3. **Physical Impossibility Detection**: Phasing algorithm prevents logically inconsistent scenarios
4. **Domain Agnostic**: Same pattern works for spatial, resource, or logical conflicts
5. **Type Safe**: Full validation of structure and values
6. **Extensible**: Easy to add new zones to vocabulary

## Limitations and Edge Cases

### 1. Same Part in Multiple Tuples

If a part appears in multiple tuples, the **last occurrence wins** (dict overwrite):

```yaml
coverage_layers:
  - parts: [chest]
    layer: 1.0
  - parts: [chest]  # Overwrites previous
    layer: 2.0
# Effective: chest → 2.0
```

**Recommendation**: Avoid duplicate parts; use validation to warn users.

### 2. Empty Coverage List

```yaml
coverage_layers: []
# Treated as "no coverage" → no conflicts with any item
```

**Design choice**: Allows items that don't participate in coverage conflicts (e.g., pure aesthetic items).

### 3. Non-Overlapping Items

Items with completely different zones will never conflict:

```yaml
# Item A: only covers upper body
coverage_layers:
  - parts: [chest, arms]
    layer: 2.0

# Item B: only covers lower body
coverage_layers:
  - parts: [legs, feet]
    layer: 2.0

# Result: No conflict (no overlapping parts)
```

This is correct behavior - items can coexist if they don't overlap spatially.

## Migration Guide

### From Gender-Specific to Gender-Agnostic

**Before (v1 - gender-specific):**
```yaml
# Separate schemas needed
schema_masculine:
  dimensions:
    - name: "body_zone"
      values: [upper_body, lower_body, feet]
    - name: "layer"
      type: integer

# Two separate catalogs
```

**After (v2 - gender-agnostic):**
```yaml
# Single unified schema
schema_v2:
  dimensions:
    - name: "coverage_layers"
      type: "part_layer_list"
      part_vocabulary: [chest, legs, feet, ...]

# Single catalog with all items
```

**Benefits**:
- 50% reduction in configuration files
- Cross-gender outfit compatibility (e.g., unisex jackets)
- Complex garments (dresses, jumpsuits) properly modeled

## Known Limitations

### 1. Stackable Accessories

The current `same_category_exclusion` rule prevents wearing any two items of the same category, which is overly restrictive for certain accessories:

**Current behavior:**
```yaml
# Rule in rules_v2.yaml
- name: "same_category_exclusion"
  type: "exclusion"
  condition:
    equals:
      field: "category"
```

**Limitations:**
- ❌ Cannot wear two necklaces (layered necklaces are common)
- ❌ Cannot wear multiple rings on different fingers
- ❌ Cannot wear multiple bracelets
- ❌ Cannot wear two earrings (only one pair allowed)

**Workaround:**
Currently, the catalog uses granular categories (`necklace`, `bracelet`, `ring`, `earrings`) which allows wearing different jewelry types together (necklace + bracelet + earrings). However, you cannot layer items within the same category.

**Future enhancement:**
Add a `stackable` boolean dimension to the schema:

```yaml
# Future schema enhancement
dimensions:
  - name: "stackable"
    type: "boolean"
    required: false
    description: "Whether multiple items of this category can be worn together"

# Catalog items
- id: "ring_001"
  attributes:
    category: "ring"
    stackable: true  # Can wear multiple rings

- id: "shirt_001"
  attributes:
    category: "shirt"
    stackable: false  # Cannot wear two shirts
```

Modify the `same_category_exclusion` rule to check `stackable`:

```yaml
# Enhanced rule (not yet implemented)
- name: "same_category_exclusion"
  type: "exclusion"
  condition:
    all:
      - equals:
          field: "category"
      - not:
          any_equals:
            field: "stackable"
            value: true
```

This enhancement is tracked for a future release. The current implementation prioritizes the core coverage-layer conflict pattern, which successfully achieves gender-agnostic wardrobe modeling.

### 2. Coverage-Layer Limitations

See **Limitations and Edge Cases** section above for:
- Same part in multiple tuples (last occurrence wins)
- Empty coverage lists (treated as "no coverage")
- Non-overlapping items (never conflict - correct behavior)

## Conclusion

The coverage-layer conflict pattern provides a robust, reusable solution for modeling spatial or logical conflicts across multiple zones with varying precedence. The phasing detection algorithm ensures physical consistency, while the granular per-part layer specification enables complex item modeling.

This pattern has been successfully implemented in the Rulate wardrobe domain (v2) and can be adapted to any domain requiring sophisticated overlap and precedence detection.

## References

- **Implementation**: `rulate/engine/operators.py` - `PartLayerConflictOperator`
- **Schema Type**: `rulate/models/schema.py` - `DimensionType.PART_LAYER_LIST`
- **Example Domain**: `examples/wardrobe/*_v2.yaml`
- **Tests**: `tests/unit/test_operators.py` - `TestPartLayerConflictOperator`
- **Integration Tests**: `tests/integration/test_wardrobe_v2_integration.py`
