# Out of Scope

Items explicitly excluded from the roadmap to prevent scope creep. These were considered but deemed not aligned with Rulate's core purpose.

## Excluded Items

### Mobile Native Apps
**Reason**: Web UI is responsive and works well on mobile. A PWA approach (see [09-mobile-and-offline.md](./09-mobile-and-offline.md)) provides most benefits without native app overhead.

### Real-time Collaborative Editing
**Reason**: Adds significant complexity (CRDT/OT algorithms, WebSocket infrastructure). Version history and comments provide sufficient collaboration for the target use case.

### Built-in Image Storage for Items
**Reason**: Out of scope for a rule engine. Users can store image URLs as string attributes if needed.

### Social Features
**Reason**: Sharing, comments, likes, and follower systems are not aligned with a rule engine's purpose. Basic sharing via URL is planned in [06-team-collaboration.md](./06-team-collaboration.md).

## Reconsidered Items

The following were initially excluded but have been reconsidered for future epics:

### Machine Learning for Rule Suggestions
**Status**: Moved to [04-intelligence-and-insights.md](./04-intelligence-and-insights.md)
**Reason**: AI/ML integration could significantly reduce manual rule creation effort.

### Natural Language Rule Parsing
**Status**: Moved to [04-intelligence-and-insights.md](./04-intelligence-and-insights.md)
**Reason**: Would dramatically improve accessibility for non-technical users.

### Integration with External Services
**Status**: Moved to [07-extensibility-and-integration.md](./07-extensibility-and-integration.md)
**Reason**: Data connectors and webhooks enable powerful workflows without making Rulate dependent on external services.
