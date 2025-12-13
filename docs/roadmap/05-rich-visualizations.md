# Rich Visualizations

> Understand compatibility through interactive visuals

## Status

- **Phase**: Planning
- **Last Updated**: December 2025

## Context

The current matrix view provides a basic compatibility visualization, but complex relationships are hard to understand at scale. Interactive visualizations help users explore compatibility patterns, understand rule effects, and communicate insights to stakeholders.

## Success Criteria

- [ ] Network graph shows item relationships interactively
- [ ] Rule evaluation flow is visualized for debugging
- [ ] Visualizations can be exported as images
- [ ] Large catalogs remain performant with virtualization

## Deliverables

### Network Graph

**Current State**: Matrix view only.

**Goal**: Interactive force-directed graph of item relationships.

**Tasks**:
- [ ] Implement D3.js force-directed graph
- [ ] Nodes represent items, edges represent compatible pairs
- [ ] Color nodes by category/attribute
- [ ] Size nodes by connectivity (more connections = larger)
- [ ] Interactive zoom, pan, and filtering
- [ ] Highlight clusters visually
- [ ] Click node to see item details
- [ ] Filter by attribute values

### Sankey Diagram

**Current State**: Rule evaluation details are text-only.

**Goal**: Visualize rule evaluation flow.

**Tasks**:
- [ ] Show how items flow through rule evaluation
- [ ] Visualize which rules pass/fail for each pair
- [ ] Debug complex rule trees visually
- [ ] Highlight bottleneck rules (most filtering)

### Timeline View

**Current State**: No temporal visualization.

**Goal**: Visualize time-based compatibility patterns.

**Tasks**:
- [ ] Show compatibility over seasons/time periods
- [ ] Gantt-style scheduling for temporal items
- [ ] Filter by time-based attributes
- [ ] Useful for domains with temporal constraints (fashion seasons, course scheduling)

### Heatmap Enhancements

**Current State**: Basic matrix heatmap with click-to-drill-down.

**Goal**: More powerful matrix visualization.

**Tasks**:
- [ ] Filter matrix by item attributes
- [ ] Export as PNG/SVG images
- [ ] Customizable color schemes
- [ ] Zoom and pan for large matrices
- [ ] Sort by different criteria (name, category, connectivity)

### 3D Visualizations

**Current State**: 2D only.

**Goal**: Explore high-dimensional item similarity.

**Tasks**:
- [ ] Apply PCA/t-SNE to reduce item attributes to 3D
- [ ] Interactive 3D scatter plot
- [ ] Color by compatibility/category
- [ ] Useful for discovering unexpected item clusters

## Dependencies

- [02-scale-and-performance.md](./02-scale-and-performance.md) - Large visualization performance depends on pagination/async

## Open Questions

- Which visualization library: D3.js, Cytoscape.js, or Three.js?
- Should visualizations be server-rendered for large datasets?
- What's the maximum item count for client-side rendering?

## Technical Notes

**Recommended libraries**:
- Network graphs: D3.js force-directed or Cytoscape.js
- Sankey diagrams: D3-sankey
- 3D visualizations: Three.js or Plotly
- Charts: Chart.js or Recharts (already may be in use)
