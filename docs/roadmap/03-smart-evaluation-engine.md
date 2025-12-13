# Smart Evaluation Engine

> More nuanced and powerful compatibility decisions

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

The current evaluation engine returns binary compatible/incompatible results. Many real-world use cases need more nuance: confidence scores, context-aware rules, and sophisticated conditional logic. This epic extends the core engine's capabilities without breaking the existing API.

## Success Criteria

- [ ] Evaluations return confidence scores (0-100) in addition to boolean compatibility
- [ ] Rules can reference external context (weather, occasion, time)
- [ ] Custom operators can be added without modifying core code
- [ ] Advanced rule types enable sophisticated decision logic

## Deliverables

### Scoring System

**Current State**: Binary compatible/incompatible only.

**Goal**: Nuanced compatibility with confidence levels.

**Tasks**:
- [ ] Define scoring algorithm (how operators contribute to scores)
- [ ] Update operators to return scores (0-100) in addition to boolean
- [ ] Add rule weights/importance for score aggregation
- [ ] Aggregate scores across multiple rules
- [ ] Update API responses to include scores alongside boolean results
- [ ] Add score thresholds for "compatible with reservations"

**Example response**:
```json
{
  "compatible": true,
  "score": 85,
  "breakdown": {
    "color_harmony": 90,
    "formality_match": 80
  }
}
```

### Context/Occasion Support

**Current State**: Rules only compare item attributes to each other.

**Goal**: Rules can reference external context.

**Tasks**:
- [ ] Define Context model (weather, occasion, time, season, etc.)
- [ ] Add context parameter to evaluation requests
- [ ] Create context-aware operators (`context_equals`, `context_in`)
- [ ] Add context filtering/selection in Web UI

**Example rule**:
```yaml
condition:
  all:
    - context_equals:
        context_key: "weather"
        value: "rainy"
    - has_different:
        field: "material"
        value: "suede"
```

### Custom Operators

**Current State**: Must edit `operators.py` to add operators.

**Goal**: Plugin system for custom operators.

**Tasks**:
- [ ] Design operator plugin interface
- [ ] Implement operator registration API
- [ ] Create operator discovery mechanism (entry points or explicit registration)
- [ ] Document how to write custom operators with examples
- [ ] Add validation for custom operator safety

### Advanced Rule Features

**Current State**: Basic condition trees with logical operators.

**Goal**: Sophisticated rule logic for complex domains.

**Tasks**:
- [ ] **Conditional Rules** - If-then-else logic within conditions
  ```yaml
  condition:
    if:
      equals: {field: "weather"}
      value: "rainy"
    then:
      has_different: {field: "material"}
      value: "suede"
  ```
- [ ] **Rule Weights** - Assign importance scores to rules
- [ ] **Temporal Rules** - Time-based conditions (season, time of day)
- [ ] **Probabilistic Rules** - Rules with confidence thresholds
- [ ] **Rule Templates** - Reusable parameterized rule patterns
- [ ] **Rule Composition** - Build complex rules from simpler named rules

## Dependencies

None - this epic extends the core engine.

## Open Questions

- Should scoring be opt-in per evaluation request, or always calculated?
- How should custom operators be sandboxed for security?
- Should context be passed per-request or stored as a named "scenario"?
