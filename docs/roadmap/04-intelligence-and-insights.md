# Intelligence & Insights

> Data-driven rule optimization and automated discovery

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

Understanding how rules perform and discovering new patterns requires visibility into system behavior. This epic adds analytics to understand rule effectiveness and introduces AI/ML capabilities to automate rule creation and optimization.

## Success Criteria

- [ ] Dashboard shows rule effectiveness metrics
- [ ] Catalog health scores identify potential issues
- [ ] AI can suggest new rules based on catalog patterns
- [ ] Natural language can be used to create simple rules

## Deliverables

### Rule Effectiveness Metrics

**Current State**: No visibility into which rules trigger most often.

**Goal**: Understand rule behavior across evaluations.

**Tasks**:
- [ ] Track how often each rule triggers (pass/fail counts)
- [ ] Identify rules that are never true (dead rules)
- [ ] Identify rules that are always true (redundant rules)
- [ ] Calculate rule coverage (what % of pairs does each rule affect?)
- [ ] Add metrics dashboard in Web UI

### Catalog Health Scores

**Current State**: No analysis of catalog quality.

**Goal**: Identify potential catalog issues.

**Tasks**:
- [ ] Calculate item connectivity (how many items each connects to)
- [ ] Identify isolated items (compatible with nothing)
- [ ] Measure category balance (over/under-represented categories)
- [ ] Generate health score summary
- [ ] Add recommendations for improving catalog

### Compatibility Trends

**Current State**: No historical tracking.

**Goal**: Track compatibility patterns over time.

**Tasks**:
- [ ] Store evaluation history (opt-in)
- [ ] Track compatibility rate changes over time
- [ ] Identify improving/degrading patterns
- [ ] Enable A/B testing of different rulesets
- [ ] Generate trend reports

### Usage Analytics

**Current State**: No usage tracking.

**Goal**: Understand how Rulate is used.

**Tasks**:
- [ ] Track most frequently evaluated pairs
- [ ] Identify performance bottlenecks (slow rules, large catalogs)
- [ ] Log API usage patterns
- [ ] Add analytics dashboard (opt-in)

### Export Reports

**Current State**: JSON/YAML export only.

**Goal**: Business-friendly reports.

**Tasks**:
- [ ] Export compatibility matrix as PDF with summary
- [ ] Export rule effectiveness report as Excel
- [ ] Include charts and visualizations in exports
- [ ] Add scheduled report generation

### AI/ML Integrations

**Current State**: All rules manually created.

**Goal**: AI-assisted rule creation and optimization.

**Tasks**:

#### Smart Rule Suggestions
- [ ] Analyze catalog to detect patterns in existing compatibilities
- [ ] Suggest new rules based on attribute correlations
- [ ] Identify missing rules for edge cases
- [ ] Learn from user corrections to improve suggestions

#### Natural Language Rule Creation
- [ ] Parse simple natural language into rule conditions
  - "Items should have different colors" → `has_different: {field: "color"}`
- [ ] Interactive rule builder with AI assistance
- [ ] Example-based rule learning ("these items are compatible because...")

#### Compatibility Predictions
- [ ] Train ML model on historical evaluations
- [ ] Predict compatibility for new items
- [ ] Provide confidence scores for predictions
- [ ] Explain predictions (which attributes matter most)

#### Anomaly Detection
- [ ] Find items that don't match typical patterns
- [ ] Detect conflicting or redundant rules
- [ ] Identify outliers in catalogs

#### Embedding-Based Similarity
- [ ] Use embeddings for semantic text field matching
- [ ] Enable "similar but not exact" matching
- [ ] Cross-domain knowledge transfer

**Recommended technologies**: OpenAI API, local LLMs (Ollama), scikit-learn, sentence-transformers

## Dependencies

- [02-scale-and-performance.md](./02-scale-and-performance.md) - Async processing for ML operations
- [03-smart-evaluation-engine.md](./03-smart-evaluation-engine.md) - Scoring system for ML confidence integration

## Open Questions

- Should analytics be opt-in or opt-out for privacy?
- What ML models/services should be supported?
- How to handle data privacy for AI features?
