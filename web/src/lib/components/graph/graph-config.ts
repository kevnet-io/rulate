/**
 * Cytoscape.js configuration for compatibility graph visualization
 *
 * This module defines:
 * - Node styles (4 categories: cluster, valid, invalid, incompatible)
 * - Edge styles (compatible, incompatible)
 * - Layout configurations (force-directed, circular, grid, hierarchical)
 */

import type { LayoutOptions, CytoscapeOptions } from "cytoscape";

/**
 * Node categories for styling
 */
export type NodeCategory = "cluster" | "valid" | "invalid" | "incompatible";

/**
 * Edge categories for styling
 */
export type EdgeCategory = "compatible" | "incompatible";

/**
 * Available layout types
 */
export type LayoutType = "force" | "circular" | "grid" | "hierarchical";

/**
 * Cytoscape stylesheet with node and edge styles
 * Aligned with Tailwind color palette
 */
export const graphStylesheet = [
  // Base node style
  {
    selector: "node",
    style: {
      label: "data(label)",
      "text-valign": "center",
      "text-halign": "center",
      "font-family": "system-ui, sans-serif",
      "font-weight": 500,
      color: "#ffffff",
      "text-outline-width": 2,
      "text-outline-color": "data(backgroundColor)",
      width: 60,
      height: 60,
      "border-width": 2,
      "border-color": "#ffffff",
      "background-color": "data(backgroundColor)",
    },
  },

  // Cluster nodes (items in current cluster)
  {
    selector: "node.cluster",
    style: {
      "background-color": "#3b82f6", // blue-500 (primary)
      "border-width": 3,
      "border-color": "#2563eb", // blue-600
      "font-size": 12,
      "text-outline-color": "#3b82f6",
    },
  },

  // Valid candidate nodes (would form valid cluster)
  {
    selector: "node.valid",
    style: {
      "background-color": "#10b981", // emerald-500
      "border-width": 2,
      "border-color": "#059669", // emerald-600
      "font-size": 11,
      "text-outline-color": "#10b981",
    },
  },

  // Invalid candidate nodes (pairwise compatible but breaks cluster rules)
  {
    selector: "node.invalid",
    style: {
      "background-color": "#f59e0b", // amber-500
      "border-width": 2,
      "border-color": "#d97706", // amber-600
      "font-size": 11,
      "text-outline-color": "#f59e0b",
    },
  },

  // Incompatible nodes (fails pairwise rules)
  {
    selector: "node.incompatible",
    style: {
      "background-color": "#f43f5e", // rose-500
      "border-width": 2,
      "border-color": "#e11d48", // rose-600
      opacity: 0.6,
      "font-size": 10,
      "text-outline-color": "#f43f5e",
    },
  },

  // Node hover state
  {
    selector: "node:active",
    style: {
      "border-width": 4,
      "border-color": "#ffffff",
      "overlay-opacity": 0.2,
    },
  },

  // Base edge style
  {
    selector: "edge",
    style: {
      width: 2,
      "line-color": "data(lineColor)",
      "line-style": "data(lineStyle)",
      opacity: "data(opacity)",
      "curve-style": "bezier",
      "target-arrow-shape": "none",
    },
  },

  // Compatible edges
  {
    selector: "edge.compatible",
    style: {
      "line-color": "#10b981", // emerald-500
      width: 2,
      opacity: 0.6,
      "line-style": "solid",
    },
  },

  // Incompatible edges
  {
    selector: "edge.incompatible",
    style: {
      "line-color": "#f43f5e", // rose-500
      width: 1,
      opacity: 0.3,
      "line-style": "dashed",
    },
  },

  // Edge hover state
  {
    selector: "edge:active",
    style: {
      width: 3,
      opacity: 1,
    },
  },

  // Highlighted edges (when hovering connected node)
  {
    selector: "edge.highlighted",
    style: {
      width: 4,
      opacity: 1,
      "z-index": 999,
    },
  },
];

/**
 * Layout configurations for different graph layouts
 */
export const layoutConfigs: Record<LayoutType, LayoutOptions> = {
  // Force-directed layout (physics-based, organic positioning)
  force: {
    name: "cose",
    animate: true,
    animationDuration: 500,
    animationEasing: "ease-out",
    nodeRepulsion: 8000,
    nodeOverlap: 20,
    idealEdgeLength: 100,
    edgeElasticity: 100,
    nestingFactor: 5,
    gravity: 80,
    numIter: 1000,
    initialTemp: 200,
    coolingFactor: 0.95,
    minTemp: 1.0,
  },

  // Circular layout (items arranged in circle)
  circular: {
    name: "circle",
    animate: true,
    animationDuration: 500,
    animationEasing: "ease-out",
    avoidOverlap: true,
    radius: undefined, // Auto-calculate
    startAngle: (3 / 2) * Math.PI, // Start at top
    clockwise: true,
    spacingFactor: 1.5,
  },

  // Grid layout (structured grid)
  grid: {
    name: "grid",
    animate: true,
    animationDuration: 500,
    animationEasing: "ease-out",
    avoidOverlap: true,
    avoidOverlapPadding: 10,
    condense: false,
    rows: undefined, // Auto-calculate
    cols: undefined, // Auto-calculate
    position: undefined, // Uses existing positions
  },

  // Hierarchical layout (breadthfirst - cluster items at top)
  hierarchical: {
    name: "breadthfirst",
    animate: true,
    animationDuration: 500,
    animationEasing: "ease-out",
    directed: false,
    padding: 10,
    avoidOverlap: true,
    spacingFactor: 1.5,
    grid: false,
    // Cluster nodes will naturally appear at top due to higher connectivity
  },
};

/**
 * Default Cytoscape options
 */
export const defaultCytoscapeOptions: Partial<CytoscapeOptions> = {
  minZoom: 0.3,
  maxZoom: 3,
  wheelSensitivity: 0.2,
  boxSelectionEnabled: false,
  selectionType: "single" as const,
  autoungrabify: false,
  autounselectify: false,
};

/**
 * Get layout configuration by type
 */
export function getLayoutConfig(layoutType: LayoutType): LayoutOptions {
  return layoutConfigs[layoutType];
}

/**
 * Get node color by category
 * Useful for legend display
 */
export const nodeCategoryColors: Record<NodeCategory, string> = {
  cluster: "#3b82f6", // blue-500
  valid: "#10b981", // emerald-500
  invalid: "#f59e0b", // amber-500
  incompatible: "#f43f5e", // rose-500
};

/**
 * Get node category label
 * Useful for legend display
 */
export const nodeCategoryLabels: Record<NodeCategory, string> = {
  cluster: "Cluster Item",
  valid: "Valid Candidate",
  invalid: "Invalid Candidate",
  incompatible: "Incompatible",
};

/**
 * Get edge color by category
 * Useful for legend display
 */
export const edgeCategoryColors: Record<EdgeCategory, string> = {
  compatible: "#10b981", // emerald-500
  incompatible: "#f43f5e", // rose-500
};

/**
 * Get edge category label
 * Useful for legend display
 */
export const edgeCategoryLabels: Record<EdgeCategory, string> = {
  compatible: "Compatible",
  incompatible: "Incompatible",
};
