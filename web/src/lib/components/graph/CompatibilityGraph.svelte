<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import cytoscape, { type Core, type NodeSingular } from "cytoscape";
  import {
    graphStylesheet,
    defaultCytoscapeOptions,
    type LayoutType,
  } from "./graph-config";
  import { getLayoutConfig } from "./graph-config";
  import type { GraphNode, GraphEdge } from "./graph-utils";

  // Props
  interface Props {
    nodes: GraphNode[];
    edges: GraphEdge[];
    layout?: LayoutType;
    onNodeClick?: (nodeId: string) => void;
    onNodeHover?: (nodeId: string | null) => void;
  }

  let {
    nodes = [],
    edges = [],
    layout = "force",
    onNodeClick,
    onNodeHover,
  }: Props = $props();

  // Cytoscape instance
  let cy: Core | null = null;
  let containerElement: HTMLDivElement;

  /**
   * Initialize Cytoscape graph
   */
  function initializeCytoscape() {
    if (!containerElement) return;

    cy = cytoscape({
      container: containerElement,
      elements: {
        nodes: nodes.map((n) => ({ data: n.data, classes: n.classes })),
        edges: edges.map((e) => ({ data: e.data, classes: e.classes })),
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      style: graphStylesheet as any,
      ...defaultCytoscapeOptions,
    });

    // Apply initial layout
    applyLayout(layout);

    // Bind event handlers
    bindEventHandlers();
  }

  /**
   * Apply layout to graph
   */
  function applyLayout(layoutType: LayoutType) {
    if (!cy) return;

    const layoutConfig = getLayoutConfig(layoutType);
    const layoutInstance = cy.layout(layoutConfig);
    layoutInstance.run();
  }

  /**
   * Update graph elements
   */
  function updateElements() {
    if (!cy) return;

    // Clear existing elements
    cy.elements().remove();

    // Add new elements
    cy.add([
      ...nodes.map((n) => ({ data: n.data, classes: n.classes })),
      ...edges.map((e) => ({ data: e.data, classes: e.classes })),
    ]);

    // Reapply layout
    applyLayout(layout);
  }

  /**
   * Bind Cytoscape event handlers
   */
  function bindEventHandlers() {
    if (!cy) return;

    // Node click
    cy.on("tap", "node", (event) => {
      const node = event.target as NodeSingular;
      if (onNodeClick) {
        onNodeClick(node.id());
      }
    });

    // Node hover (mouseover)
    cy.on("mouseover", "node", (event) => {
      const node = event.target as NodeSingular;
      if (onNodeHover) {
        onNodeHover(node.id());
      }
    });

    // Node hover out (mouseout)
    cy.on("mouseout", "node", () => {
      if (onNodeHover) {
        onNodeHover(null);
      }
    });
  }

  /**
   * Zoom in
   */
  export function zoomIn() {
    if (!cy) return;
    const currentZoom = cy.zoom();
    cy.zoom({
      level: currentZoom * 1.2,
      renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
    });
  }

  /**
   * Zoom out
   */
  export function zoomOut() {
    if (!cy) return;
    const currentZoom = cy.zoom();
    cy.zoom({
      level: currentZoom / 1.2,
      renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
    });
  }

  /**
   * Fit graph to container
   */
  export function fit() {
    if (!cy) return;
    cy.fit(undefined, 50); // 50px padding
  }

  /**
   * Change layout
   */
  export function changeLayout(newLayout: LayoutType) {
    applyLayout(newLayout);
  }

  /**
   * Get node position (for testing)
   */
  export function getNodePosition(
    nodeId: string,
  ): { x: number; y: number } | null {
    if (!cy) return null;
    const node = cy.getElementById(nodeId);
    if (!node || node.length === 0) return null;
    return node.position();
  }

  /**
   * Lifecycle: Initialize on mount
   */
  onMount(() => {
    initializeCytoscape();
  });

  /**
   * Lifecycle: Watch for nodes/edges changes
   */
  $effect(() => {
    // Trigger when nodes or edges change
    if (cy && (nodes.length > 0 || edges.length > 0)) {
      updateElements();
    }
  });

  /**
   * Lifecycle: Watch for layout changes
   */
  $effect(() => {
    // Trigger when layout changes
    if (cy) {
      applyLayout(layout);
    }
  });

  /**
   * Lifecycle: Cleanup on unmount
   */
  onDestroy(() => {
    if (cy) {
      cy.destroy();
      cy = null;
    }
  });
</script>

<div
  bind:this={containerElement}
  class="graph-container w-full h-full min-h-[400px] bg-background border border-border rounded-md"
  role="img"
  aria-label="Compatibility graph visualization"
></div>

<style>
  .graph-container {
    position: relative;
  }
</style>
