# Team Collaboration

> Enable teams to work together on rulesets

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

Rulate currently operates as a single-user system. For organizations, multiple team members need to collaborate on rulesets, track changes, and manage access. This epic adds multi-user capabilities and collaboration features.

## Success Criteria

- [ ] Users can log in and own their catalogs
- [ ] Role-based access controls who can edit vs view
- [ ] Change history is tracked with attribution
- [ ] Teams can share and collaborate on rulesets

## Deliverables

### Authentication & Authorization

**Current State**: No authentication (single-user system).

**Goal**: Secure multi-user access.

**Tasks**:
- [ ] Add user registration and login
- [ ] Implement JWT token authentication
- [ ] Add role-based access control (RBAC): viewer, editor, admin
- [ ] Assign catalog/ruleset ownership
- [ ] Add API key authentication for programmatic access
- [ ] Consider OAuth integration (Google, GitHub)

### Bulk Operations

**Current State**: Single-item operations only.

**Goal**: Efficient batch operations.

**Tasks**:
- [ ] Bulk delete items (select multiple, delete all)
- [ ] Bulk edit attributes (change field for multiple items)
- [ ] CSV import with field mapping wizard
- [ ] CSV export for spreadsheet workflows

### Saved Queries/Filters

**Current State**: Filters reset on page navigation.

**Goal**: Persistent, shareable query presets.

**Tasks**:
- [ ] Save frequently used evaluation configurations
- [ ] Name and organize saved presets
- [ ] Share saved queries with team members
- [ ] Quick-apply from dropdown

### User Preferences

**Current State**: No persistent preferences.

**Goal**: Personalized experience.

**Tasks**:
- [ ] Dark mode toggle
- [ ] Default output format preference
- [ ] UI density options (compact vs comfortable)
- [ ] Persistent settings in localStorage (pre-auth) or user profile (post-auth)

### Comments & Annotations

**Current State**: No commenting capability.

**Goal**: Contextual team communication.

**Tasks**:
- [ ] Add comments to items, rules, and schemas
- [ ] Mention team members in comments
- [ ] Comment threads with replies
- [ ] Activity feed showing recent comments

### Version History

**Current State**: No change tracking.

**Goal**: Full audit trail and rollback.

**Tasks**:
- [ ] Track all changes to rulesets and catalogs
- [ ] Store change attribution (who changed what, when)
- [ ] Diff view to compare versions side-by-side
- [ ] Rollback to previous versions
- [ ] Fork/clone catalogs for experimentation

### Sharing

**Current State**: No sharing mechanism.

**Goal**: Easy collaboration without full accounts.

**Tasks**:
- [ ] Generate shareable URLs for specific evaluations
- [ ] Public vs private link options
- [ ] Export to Markdown reports
- [ ] Embed visualizations in external tools

## Dependencies

- [01-production-ready.md](./01-production-ready.md) - Security infrastructure needed for auth

## Open Questions

- Should we support SSO/SAML for enterprise?
- How granular should permissions be (catalog-level vs item-level)?
- What's the data retention policy for version history?
