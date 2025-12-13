# Developer Adoption

> Make it easy for developers to learn and contribute

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

Good documentation and examples lower the barrier to entry for new users and contributors. This epic focuses on making Rulate accessible to developers through comprehensive documentation, diverse examples, and smooth onboarding experiences.

## Success Criteria

- [ ] New users can get started in under 10 minutes
- [ ] At least 3 domain examples beyond wardrobe
- [ ] Architecture is visually documented
- [ ] Contributors can set up dev environment instantly

## Deliverables

### Architecture Documentation

**Current State**: Text descriptions in SPECIFICATION.md and CLAUDE.md.

**Goal**: Visual understanding of system design.

**Tasks**:
- [ ] Create system architecture diagram (layers, components)
- [ ] Create data flow diagram (request → response)
- [ ] Create database ERD (entity relationships)
- [ ] Create evaluation algorithm flowchart
- [ ] Add diagrams to `docs/ARCHITECTURE.md`
- [ ] Link from README

**Format options**: Mermaid.js (renders in GitHub), Excalidraw, Draw.io

### Domain Examples

**Current State**: Only wardrobe example exists.

**Goal**: Demonstrate domain-agnostic nature with templates.

**Tasks**:

#### Recipe Ingredients (`examples/recipes/`)
- [ ] Schema: ingredient type, cuisine, dietary restrictions, flavor profile
- [ ] Rules: Flavor compatibility, dietary constraints
- [ ] Catalog: 15-20 common ingredients

#### Course Prerequisites (`examples/education/`)
- [ ] Schema: subject, level, credits, semester
- [ ] Rules: Prerequisite chains, scheduling conflicts
- [ ] Catalog: 10-15 courses

#### Team Skills Matching (`examples/teams/`)
- [ ] Schema: role, skills, experience level, availability
- [ ] Rules: Complementary skills, team size constraints
- [ ] Catalog: 10-12 team member profiles

Each example should include:
- README explaining the domain
- Complete schema, rules, and catalog files
- Sample CLI commands to evaluate

### API Documentation Improvements

**Current State**: Auto-generated OpenAPI docs.

**Goal**: Developer-friendly API reference.

**Tasks**:
- [ ] Add request/response examples to all endpoints
- [ ] Document error codes and messages
- [ ] Add authentication documentation (when implemented)
- [ ] Create interactive examples (Swagger "Try it out")
- [ ] Add rate limit documentation (when implemented)

### User Guide & Tutorials

**Current State**: README has quick start but lacks depth.

**Goal**: Comprehensive learning path.

**Tasks**:
- [ ] Step-by-step "Getting Started" tutorial
- [ ] "Your First Schema" guide
- [ ] "Writing Effective Rules" guide
- [ ] Common use case walkthroughs
- [ ] Troubleshooting guide
- [ ] FAQ section

### Interactive Tutorials

**Current State**: No in-app guidance.

**Goal**: Hands-on learning within the app.

**Tasks**:
- [ ] In-app walkthrough for first-time users
- [ ] Interactive sandbox environment (reset button, example data)
- [ ] Jupyter notebooks with examples
- [ ] Video screencasts for complex features
- [ ] Consider live demo instance

### Dev Container

**Current State**: Manual environment setup.

**Goal**: Instant development environment.

**Tasks**:
- [ ] Create `.devcontainer/devcontainer.json`
- [ ] Include Python + Node.js environment
- [ ] Pre-install all dependencies
- [ ] Auto-install recommended VS Code extensions
- [ ] Document usage in CONTRIBUTING.md

### Changelog Automation

**Current State**: Manual changelog updates.

**Goal**: Automated release notes.

**Tasks**:
- [ ] Adopt conventional commit message format
- [ ] Integrate `conventional-changelog` or `release-please`
- [ ] Automatic CHANGELOG.md generation on release
- [ ] Semantic versioning based on commit types

## Dependencies

None - this epic can proceed independently.

## Open Questions

- Should tutorials be in docs or a separate documentation site?
- What video hosting platform for screencasts?
- Is a live demo instance worth the hosting cost?
