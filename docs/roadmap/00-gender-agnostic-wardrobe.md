# Gender-Agnostic Wardrobe Enhancement

**Status:** In Progress
**Priority:** Immediate
**Complexity:** High

## Overview

Comprehensive redesign of the wardrobe example domain to be gender-agnostic and physically accurate, with clear separation between physical compatibility (pairwise rules) and aesthetic compatibility (cluster rules).

## Motivation

The current `examples/wardrobe/` domain has several limitations:

1. **Gender bias**: Only models masculine-leaning/male-traditional clothing items
2. **Mixed concerns**: Pairwise rules conflate physical and aesthetic compatibility
3. **Oversimplified layering**: Single `layer` field per item can't model complex garments (e.g., bodycon-top/flowy-bottom dress)
4. **Body coverage ambiguity**: Simple `body_zone` enum can't distinguish between short sleeve vs long sleeve, shorts vs pants, etc.

## Goals

1. **Gender inclusivity**: Catalog with 50+ diverse items across masculine, feminine, and unisex clothing
2. **Physical accuracy**: Model real-world clothing compatibility based on coverage and layering
3. **Separation of concerns**: Pairwise rules = "Can items physically be worn together?", Cluster rules = "Does this outfit make aesthetic sense?"
4. **Granular coverage**: Explicit body part mapping (upper_arm vs lower_arm, upper_leg vs lower_leg, etc.)
5. **Per-part layering**: Items can specify different layers for different body parts (e.g., dress with tight bodice, flowy skirt)

## Technical Design

### New Dimension Type: `part_layer_list`

A new dimension type that represents coverage-layer tuples:

```yaml
coverage_layers:
  - parts: [chest, waist, upper_back, lower_back]
    layer: 2.0
  - parts: [hips, upper_leg, lower_leg, ankle]
    layer: 1.5  # Tighter fit = can go under other layer 2.0 items
```

**Structure:**
- Each tuple specifies which body parts are covered and at what layer
- Layer values are decimals (0.0, 1.0, 1.5, 2.0, etc.) for granularity
- Same item can have different layers for different body parts

**Validation:**
- `parts` must be a non-empty list of strings
- `layer` must be a number >= 0
- Body part strings should match schema's vocabulary (optional validation)

### New Operator: `PartLayerConflictOperator`

Generic operator for detecting coverage-layer conflicts between items.

**Algorithm:**
1. Extract all (part, layer) tuples from both items
2. Find overlapping parts (parts present in both items)
3. If no overlaps → no conflict (compatible)
4. For each overlapping part:
   - If same layer → **conflict** (can't stack at same layer)
   - Record whether item_a > item_b or item_a < item_b
5. Check consistent ordering: All overlaps must have same relationship (all A>B or all A<B)
6. If inconsistent ordering → **conflict** (phasing violation)

**Example - No Phasing (Valid):**
```
Item A: chest(2.0), legs(2.0)
Item B: chest(1.0), legs(1.0)
→ A > B on chest AND A > B on legs → Consistent → Compatible
```

**Example - Phasing (Invalid):**
```
Item A: chest(2.0), legs(1.0)
Item B: chest(1.0), legs(2.0)
→ A > B on chest BUT A < B on legs → Inconsistent → Conflict!
```

This prevents impossible configurations where A is simultaneously over and under B.

### Body Parts Vocabulary

Comprehensive coverage of human body:

**Head/Face:**
- `head`, `face`, `ears`, `neck`

**Torso:**
- `shoulders`, `chest`, `upper_back`, `lower_back`, `waist`, `hips`

**Arms:**
- `upper_arm`, `lower_arm`, `wrist`, `hands`, `fingers`

**Legs:**
- `groin`, `upper_leg`, `lower_leg`, `ankle`, `feet`, `toes`

This allows distinguishing:
- Short sleeve (`shoulders`, `upper_arm`) vs long sleeve (`shoulders`, `upper_arm`, `lower_arm`)
- Shorts (`hips`, `upper_leg`) vs pants (`hips`, `upper_leg`, `lower_leg`)
- Gloves (`hands`, `fingers`) vs wrist gloves (`wrist`, `hands`, `fingers`)

### Layer Numbering Convention

**0.0-0.9: Skin contact undergarments**
- 0.0: Underwear, bras
- 0.5: Body shapers, compression garments

**1.0-1.9: Light undergarments**
- 1.0: Undershirts, slips, tights (thin)
- 1.5: Leggings (thick), thermal underwear

**2.0-2.9: Base garments**
- 2.0: Shirts, pants, skirts, dresses (standard fit)
- 2.5: Loose-fit pants, flowy skirts

**3.0-3.9: Mid layers**
- 3.0: Sweaters, vests, cardigans
- 3.5: Thick hoodies

**4.0-4.9: Outer layers**
- 4.0: Light jackets, blazers
- 4.5: Heavy coats, parkas

**5.0+: Extreme outer layers**
- 5.0: Winter overcoats, ponchos

### Schema Changes (V2)

**Remove:**
- `body_zone` dimension (replaced by `coverage_layers`)
- `layer` dimension (incorporated into `coverage_layers`)

**Add:**
- `coverage_layers` dimension (type: `part_layer_list`)

**Expand:**
- `category` values: Add `dress`, `skirt`, `blouse`, `bra`, `underwear`, `tights`, `leggings`, `boots`, `heels`, `jewelry`, `sweater`, `vest`, `cardigan`, `shorts`, etc.

**Keep unchanged:**
- `formality`, `colors`, `season`, `style` (aesthetic dimensions for cluster rules)

### Pairwise Rules Redesign (V2)

**Physical compatibility only:**

1. **Coverage-layer conflict** (new operator)
   - Type: `exclusion`
   - Items incompatible if they have overlapping coverage at same layer or phasing violations

2. **Same category exclusion** (keep from v1)
   - Type: `exclusion`
   - Can't wear two items of exact same category (e.g., two pants, two dresses)
   - Note: This might need refinement (can you wear two necklaces? two rings?)

**Remove from pairwise (move to cluster):**
- `formality_matching` → cluster rule
- `season_compatibility` → cluster rule

### Cluster Rules Enhancement (V2)

**Add from pairwise:**
- Formality consistency across outfit
- Season compatibility across outfit

**Keep existing:**
- Minimum outfit size
- Cover multiple zones
- Maximum outfit size

**Potential additions:**
- Color coordination rules
- Style coherence rules (e.g., don't mix athletic + formal)
- Pattern clashing rules

### Catalog V2 (50+ Items)

**Masculine/Unisex (20+ items):**
- Underwear: boxers, briefs, undershirt
- Pants: jeans, dress slacks, chinos, shorts, cargo pants
- Shirts: t-shirt, polo, oxford, button-down, tank top
- Outerwear: blazer, denim jacket, leather jacket, hoodie, suit jacket
- Shoes: sneakers, oxfords, loafers, boots
- Accessories: belt, tie, watch, hat, socks

**Feminine/Unisex (20+ items):**
- Underwear: bra, underwear, slip
- Bottoms: skirt (pencil, A-line, maxi), dress pants, leggings
- Tops: blouse, camisole, tank top, turtleneck
- Dresses: bodycon dress, cocktail dress, sundress, maxi dress
- Tights/Hosiery: sheer tights, opaque tights, stockings
- Outerwear: cardigan, blazer, trench coat
- Shoes: heels, flats, boots, sandals
- Accessories: jewelry (necklace, earrings, bracelet), scarf, belt

**Gender-neutral (10+ items):**
- T-shirts, jeans, sneakers, jackets, accessories

## Implementation Plan

### Phase 1: Core Engine (Estimated: 2-3 development sessions)

1. **Add `part_layer_list` dimension type**
   - File: `rulate/models/schema.py`
   - Add to `DimensionType` enum
   - Implement validation in `Dimension.validate_value()`
   - Test with unit tests

2. **Implement `PartLayerConflictOperator`**
   - File: `rulate/engine/operators.py`
   - Implement overlapping parts detection
   - Implement consistent ordering check
   - Register in `OPERATOR_REGISTRY`
   - Comprehensive unit tests (including phasing scenarios)

3. **Update condition evaluator**
   - File: `rulate/engine/condition_evaluator.py`
   - Ensure new operator is discoverable
   - Add any special parsing if needed

### Phase 2: Example Domain V2 (Estimated: 3-4 development sessions)

4. **Create `schema_v2.yaml`**
   - Define `coverage_layers` dimension
   - Document body parts vocabulary
   - Remove old `body_zone` and `layer`
   - Expand `category` values

5. **Create `rules_v2.yaml`**
   - Implement coverage-layer conflict rule
   - Keep category exclusion rule
   - Remove aesthetic rules

6. **Create `cluster_rules_v2.yaml`**
   - Move formality/season rules from pairwise
   - Keep existing cluster constraints
   - Add new aesthetic rules as needed

7. **Create `catalog_v2.yaml` - Phase 1 (30 items)**
   - Start with core diverse items
   - Ensure good coverage of:
     - Masculine/feminine/unisex
     - Undergarments/base/outer layers
     - All major categories
   - Test with engine

8. **Expand `catalog_v2.yaml` - Phase 2 (50+ items)**
   - Add remaining items for comprehensiveness
   - Edge cases (complex layering, special fits)
   - Variety in formality/style/season

### Phase 3: Testing & Validation (Estimated: 2 sessions)

9. **Unit tests for new dimension type**
   - File: `tests/unit/test_schema.py`
   - Valid `part_layer_list` values
   - Invalid values (wrong structure, types)
   - Edge cases

10. **Unit tests for new operator**
    - File: `tests/unit/test_operators.py`
    - No overlap → compatible
    - Same layer overlap → conflict
    - Different layer overlap → compatible
    - Phasing scenarios → conflict
    - Consistent ordering → compatible

11. **Integration tests with V2 files**
    - File: `tests/integration/test_wardrobe_v2.py` (new)
    - Load schema/rules/catalog v2
    - Test known compatible pairs
    - Test known incompatible pairs
    - Test phasing violations
    - Test cluster evaluation with v2

### Phase 4: Documentation (Estimated: 1-2 sessions)

12. **Update `SPECIFICATION.md`**
    - Document `part_layer_list` type
    - Document `PartLayerConflictOperator`
    - Add to operator reference table

13. **Create pattern documentation**
    - File: `docs/patterns/coverage-layer-conflicts.md`
    - Explain the pattern
    - Show how to apply to other domains
    - Include examples (wardrobe, furniture, etc.)

14. **Update `CLAUDE.md`**
    - Reference v2 as the canonical example
    - Note v1 kept for backward compatibility
    - Explain coverage-layer pattern

### Phase 5: Validation (Estimated: 1 session)

15. **CLI testing**
    - Test validation: `rulate validate schema examples/wardrobe/schema_v2.yaml`
    - Test evaluation: `rulate evaluate pair <id1> <id2> --catalog examples/wardrobe/catalog_v2.yaml --rules examples/wardrobe/rules_v2.yaml`
    - Test matrix generation with v2

16. **Full test suite**
    - Run `make check-all`
    - Ensure all tests pass
    - Verify coverage maintained/improved

## Success Criteria

- [ ] `part_layer_list` dimension type implemented with validation
- [ ] `PartLayerConflictOperator` correctly detects conflicts and phasing violations
- [ ] Unit tests achieve >95% coverage on new code
- [ ] `schema_v2.yaml` defines comprehensive body parts vocabulary
- [ ] `rules_v2.yaml` contains only physical compatibility rules
- [ ] `cluster_rules_v2.yaml` contains all aesthetic constraints
- [ ] `catalog_v2.yaml` has 50+ diverse items (masculine, feminine, unisex)
- [ ] Integration tests validate v2 evaluation works correctly
- [ ] Documentation explains the pattern for reuse in other domains
- [ ] All existing tests continue to pass (v1 remains functional)
- [ ] CLI tool works seamlessly with v2 files

## Future Enhancements

**Not in initial scope, but possible later:**

1. **Fit attribute**: Add `tight`, `normal`, `loose`, `puffy` to coverage-layer tuples for even more precision
2. **Material constraints**: Can't wear two leather items on same zone (sweating)
3. **Color coordination**: Smart color matching in cluster rules
4. **Occasion-based outfits**: Cluster rules for "work", "gym", "formal event"
5. **Weather constraints**: Temperature ranges, rain compatibility
6. **Accessory stacking**: Special rules for jewelry, belts, watches (can wear multiple)

## Migration Path

**For users of v1:**
- v1 files (`schema.yaml`, `rules.yaml`, `catalog.yaml`) remain unchanged and functional
- v2 files are additive, not replacement
- Both versions serve as examples of different modeling approaches
- No breaking changes to core engine (new type and operator are additions)

**For developers:**
- Pattern documented for applying coverage-layer approach to other domains
- Clear guidance on when to use simple `body_zone` (v1) vs granular `coverage_layers` (v2)

## Timeline

**Estimated total:** 9-12 development sessions (20-30 hours)

- **Week 1**: Core engine implementation (Phase 1)
- **Week 2**: Schema/Rules v2 + initial catalog (Phase 2.1)
- **Week 3**: Complete catalog + testing (Phase 2.2 + Phase 3)
- **Week 4**: Documentation + validation (Phase 4 + Phase 5)

## Related Roadmap Items

- None currently (this is a new enhancement)
- May inform future work on:
  - Other example domains using coverage-layer pattern
  - Visual outfit builder in web UI
  - AI-assisted outfit suggestions

## Notes

- This enhancement demonstrates Rulate's flexibility for modeling complex physical relationships
- The coverage-layer pattern is a reusable design pattern for spatial compatibility problems
- Keeps pairwise rules focused on "can these coexist" vs cluster rules on "should these be grouped"
- Gender-agnostic design makes the domain more inclusive and realistic
