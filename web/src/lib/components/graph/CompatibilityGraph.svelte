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

  // Tooltip state
  let tooltipVisible = $state(false);
  let tooltipX = $state(0);
  let tooltipY = $state(0);
  let tooltipContent = $state("");
  let tooltipCategory = $state("");

  // Performance: debounce timer
  let updateTimer: ReturnType<typeof setTimeout> | null = null;

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
   * Update graph elements (debounced for performance)
   */
  function updateElements() {
    if (!cy) return;

    // Debounce updates to avoid excessive re-renders
    if (updateTimer) {
      clearTimeout(updateTimer);
    }

    updateTimer = setTimeout(() => {
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
    }, 100); // 100ms debounce
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

    // Node hover (mouseover) - show tooltip and highlight edges
    cy.on("mouseover", "node", (event) => {
      const node = event.target as NodeSingular;

      // Show tooltip
      const nodeData = node.data();
      tooltipContent = nodeData.label || nodeData.id;
      tooltipCategory = nodeData.category || "";

      // Position tooltip near the cursor
      const renderedPosition = node.renderedPosition();
      tooltipX = renderedPosition.x;
      tooltipY = renderedPosition.y - 40; // Above the node
      tooltipVisible = true;

      // Highlight connected edges
      const connectedEdges = node.connectedEdges();
      connectedEdges.addClass("highlighted");

      // Callback
      if (onNodeHover) {
        onNodeHover(node.id());
      }
    });

    // Node hover out (mouseout) - hide tooltip and remove highlight
    cy.on("mouseout", "node", (event) => {
      const node = event.target as NodeSingular;

      // Hide tooltip
      tooltipVisible = false;

      // Remove edge highlighting
      const connectedEdges = node.connectedEdges();
      connectedEdges.removeClass("highlighted");

      // Callback
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
    // Clear any pending updates
    if (updateTimer) {
      clearTimeout(updateTimer);
    }

    // Destroy Cytoscape instance
    if (cy) {
      cy.destroy();
      cy = null;
    }
  });
</script>

<div class="relative">
  <div
    bind:this={containerElement}
    class="graph-container w-full h-full min-h-[400px] bg-background border border-border rounded-md"
    role="img"
    aria-label="Compatibility graph visualization"
  ></div>

  <!-- Tooltip -->
  {#if tooltipVisible}
    <div
      class="absolute z-10 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg shadow-lg pointer-events-none whitespace-nowrap"
      style="left: {tooltipX}px; top: {tooltipY}px; transform: translate(-50%, -100%);"
    >
      <div class="flex items-center gap-2">
        <div
          class="w-2 h-2 rounded-full"
          class:bg-blue-500={tooltipCategory === "cluster"}
          class:bg-emerald-500={tooltipCategory === "valid"}
          class:bg-amber-500={tooltipCategory === "invalid"}
          class:bg-rose-500={tooltipCategory === "incompatible"}
        ></div>
        <span>{tooltipContent}</span>
      </div>
      <div
        class="absolute w-2 h-2 bg-gray-900 transform rotate-45"
        style="left: 50%; bottom: -4px; transform: translateX(-50%) rotate(45deg);"
      ></div>
    </div>
  {/if}
</div>

<style>
  .graph-container {
    position: relative;
  }
</style>
