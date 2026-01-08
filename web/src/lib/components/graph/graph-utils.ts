/**
 * Utility functions for transforming data into Cytoscape graph format
 */

import type { Item, EvaluationMatrix, CandidateResult } from "$lib/api/client";
import type { NodeCategory, EdgeCategory } from "./graph-config";

/**
 * Cytoscape node data structure
 */
export interface GraphNode {
  data: {
    id: string;
    label: string;
    category: NodeCategory;
    backgroundColor: string;
  };
  classes: string;
}

/**
 * Cytoscape edge data structure
 */
export interface GraphEdge {
  data: {
    id: string;
    source: string;
    target: string;
    compatible: boolean;
    lineColor: string;
    lineStyle: "solid" | "dashed";
    opacity: number;
  };
  classes: string;
}

/**
 * Graph data returned by transformToGraphData
 */
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/**
 * Get node category colors (matching graph-config.ts)
 */
const NODE_COLORS: Record<NodeCategory, string> = {
  cluster: "#3b82f6", // blue-500
  valid: "#10b981", // emerald-500
  invalid: "#f59e0b", // amber-500
  incompatible: "#f43f5e", // rose-500
};

/**
 * Filter visible items based on current cluster, candidates, and toggle state
 *
 * @param clusterItemIds - Item IDs in current cluster
 * @param validCandidates - Candidates that would form valid cluster
 * @param invalidCandidates - Candidates that are pairwise compatible but break cluster rules
 * @param incompatibleCandidates - Candidates that fail pairwise rules
 * @param showIncompatible - Whether to include incompatible items
 * @returns Array of visible item IDs
 */
export function filterVisibleItems(
  clusterItemIds: string[],
  validCandidates: CandidateResult[],
  invalidCandidates: CandidateResult[],
  incompatibleCandidates: CandidateResult[],
  showIncompatible: boolean,
): string[] {
  const visibleIds = new Set<string>();

  // Always include cluster items
  clusterItemIds.forEach((id) => visibleIds.add(id));

  // Always include valid and invalid candidates
  validCandidates.forEach((c) => visibleIds.add(c.item_id));
  invalidCandidates.forEach((c) => visibleIds.add(c.item_id));

  // Conditionally include incompatible candidates
  if (showIncompatible) {
    incompatibleCandidates.forEach((c) => visibleIds.add(c.item_id));
  }

  return Array.from(visibleIds);
}

/**
 * Build edges from evaluation matrix for visible items
 *
 * @param matrix - Full pairwise evaluation matrix
 * @param visibleItemIds - Item IDs to include in graph
 * @param showIncompatible - Whether to include incompatible edges
 * @returns Array of graph edges
 */
export function buildEdgesFromMatrix(
  matrix: EvaluationMatrix | null,
  visibleItemIds: string[],
  showIncompatible: boolean,
): GraphEdge[] {
  if (!matrix || !matrix.results) {
    return [];
  }

  const edges: GraphEdge[] = [];
  const visibleSet = new Set(visibleItemIds);

  for (const result of matrix.results) {
    // Only include edges between visible items
    if (!visibleSet.has(result.item1_id) || !visibleSet.has(result.item2_id)) {
      continue;
    }

    // Skip incompatible edges if toggle is off
    if (!result.compatible && !showIncompatible) {
      continue;
    }

    const edgeCategory: EdgeCategory = result.compatible
      ? "compatible"
      : "incompatible";

    edges.push({
      data: {
        id: `${result.item1_id}-${result.item2_id}`,
        source: result.item1_id,
        target: result.item2_id,
        compatible: result.compatible,
        lineColor: result.compatible ? "#10b981" : "#f43f5e",
        lineStyle: result.compatible ? "solid" : "dashed",
        opacity: result.compatible ? 0.6 : 0.3,
      },
      classes: edgeCategory,
    });
  }

  return edges;
}

/**
 * Categorize a candidate based on its validation status
 *
 * @param candidate - Candidate result from API
 * @returns Node category
 */
function categorizeCandidateNode(candidate: CandidateResult): NodeCategory {
  if (!candidate.is_pairwise_compatible) {
    return "incompatible";
  }
  if (candidate.cluster_if_added.is_valid) {
    return "valid";
  }
  return "invalid";
}

/**
 * Transform items, matrix, cluster, and candidates into Cytoscape graph data
 *
 * @param items - All items in catalog
 * @param matrix - Pairwise evaluation matrix
 * @param clusterItemIds - Item IDs in current cluster
 * @param candidates - Candidate evaluation results
 * @param showIncompatible - Whether to include incompatible items/edges
 * @returns Graph data with nodes and edges
 */
export function transformToGraphData(
  items: Item[],
  matrix: EvaluationMatrix | null,
  clusterItemIds: string[],
  candidates: CandidateResult[] | null,
  showIncompatible: boolean,
): GraphData {
  // Build item lookup map
  const itemMap = new Map<string, Item>();
  items.forEach((item) => {
    itemMap.set(item.item_id, item);
  });

  // Categorize candidates
  const validCandidates: CandidateResult[] = [];
  const invalidCandidates: CandidateResult[] = [];
  const incompatibleCandidates: CandidateResult[] = [];

  if (candidates) {
    for (const candidate of candidates) {
      const category = categorizeCandidateNode(candidate);
      if (category === "valid") {
        validCandidates.push(candidate);
      } else if (category === "invalid") {
        invalidCandidates.push(candidate);
      } else {
        incompatibleCandidates.push(candidate);
      }
    }
  }

  // Determine visible items
  const visibleItemIds = filterVisibleItems(
    clusterItemIds,
    validCandidates,
    invalidCandidates,
    incompatibleCandidates,
    showIncompatible,
  );

  // Build nodes
  const nodes: GraphNode[] = [];
  const clusterSet = new Set(clusterItemIds);

  for (const itemId of visibleItemIds) {
    const item = itemMap.get(itemId);
    if (!item) continue;

    // Determine node category
    let category: NodeCategory;
    if (clusterSet.has(itemId)) {
      category = "cluster";
    } else {
      // Find candidate to determine category
      const candidate = candidates?.find((c) => c.item_id === itemId);
      category = candidate ? categorizeCandidateNode(candidate) : "valid";
    }

    nodes.push({
      data: {
        id: itemId,
        label: item.name,
        category,
        backgroundColor: NODE_COLORS[category],
      },
      classes: category,
    });
  }

  // Build edges
  const edges = buildEdgesFromMatrix(matrix, visibleItemIds, showIncompatible);

  return { nodes, edges };
}

/**
 * Get item name from item ID
 * Helper for displaying item names in tooltips/labels
 *
 * @param itemId - Item ID to look up
 * @param items - Array of all items
 * @returns Item name or itemId if not found
 */
export function getItemName(itemId: string, items: Item[]): string {
  const item = items.find((i) => i.item_id === itemId);
  return item ? item.name : itemId;
}
