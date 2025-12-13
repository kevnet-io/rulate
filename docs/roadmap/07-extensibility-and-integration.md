# Extensibility & Integration

> Connect Rulate to external systems

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

Rulate is most powerful when integrated into larger workflows. This epic adds extension points for external systems to interact with Rulate, import data from various sources, and build custom functionality without modifying core code.

## Success Criteria

- [ ] External systems can subscribe to Rulate events
- [ ] Custom operators can be added via plugins
- [ ] Data can be imported from common sources (spreadsheets, databases)
- [ ] Rulate can be embedded in automated workflows

## Deliverables

### Webhooks & Events

**Current State**: No event notification system.

**Goal**: Real-time integration with external systems.

**Tasks**:
- [ ] Define event types (item_created, evaluation_completed, rule_changed, etc.)
- [ ] Add webhook subscription management API
- [ ] Implement webhook delivery with retry logic
- [ ] Support webhook authentication (HMAC signatures)
- [ ] Add webhook testing/debugging tools

**Example webhook payload**:
```json
{
  "event": "evaluation_completed",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "catalog": "wardrobe",
    "item1": "shirt_001",
    "item2": "pants_002",
    "compatible": true
  }
}
```

### Plugin System

**Current State**: Must modify source code to add operators.

**Goal**: Community-extensible operator ecosystem.

**Tasks**:
- [ ] Design plugin architecture (Python entry points or explicit registration)
- [ ] Create plugin interface specification
- [ ] Implement plugin discovery and loading
- [ ] Add plugin sandboxing for security
- [ ] Create plugin configuration UI in Web UI
- [ ] Document plugin development guide
- [ ] Consider plugin marketplace/registry

**Plugin example**:
```python
from rulate.plugins import OperatorPlugin

class SemanticSimilarityPlugin(OperatorPlugin):
    name = "semantic_similar"

    def evaluate(self, item1, item2, field, threshold=0.8):
        # Custom logic using embeddings
        return similarity > threshold, f"Similarity: {similarity}"
```

### Data Connectors

**Current State**: Manual JSON/YAML import only.

**Goal**: Import data from common sources.

**Tasks**:

#### Google Sheets Connector
- [ ] OAuth integration with Google
- [ ] Map spreadsheet columns to schema dimensions
- [ ] Periodic sync or one-time import options

#### Airtable Integration
- [ ] API key authentication
- [ ] Base/table selection UI
- [ ] Field mapping wizard

#### CSV Import Wizard
- [ ] Column mapping interface
- [ ] Data type detection
- [ ] Preview before import
- [ ] Handle duplicates (skip, update, fail)

#### SQL Database Sync
- [ ] Connect to PostgreSQL, MySQL, SQLite
- [ ] Table/view selection
- [ ] Query-based import
- [ ] Scheduled sync

#### REST API Polling
- [ ] Configure external API endpoint
- [ ] Define data transformation
- [ ] Polling schedule
- [ ] Incremental updates

## Dependencies

- [01-production-ready.md](./01-production-ready.md) - Security for webhook authentication
- [06-team-collaboration.md](./06-team-collaboration.md) - Auth needed for connector OAuth

## Open Questions

- Should plugins run in-process or in isolated containers?
- What's the security model for data connectors (credential storage)?
- Should there be rate limits on webhook deliveries?
