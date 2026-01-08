/**
 * Unit tests for graph utility functions
 */

import { describe, it, expect } from "vitest";
import {
  filterVisibleItems,
  buildEdgesFromMatrix,
  transformToGraphData,
  getItemName,
} from "./graph-utils";
import type {
  Item,
  EvaluationMatrix,
  CandidateResult,
  RuleEvaluation,
} from "$lib/api/client";

// Test fixtures
const mockItems: Item[] = [
  {
    item_id: "item1",
    name: "Item One",
    attributes: {},
  },
  {
    item_id: "item2",
    name: "Item Two",
    attributes: {},
  },
  {
    item_id: "item3",
    name: "Item Three",
    attributes: {},
  },
  {
    item_id: "item4",
    name: "Item Four",
    attributes: {},
  },
];

const mockRuleEvaluations: RuleEvaluation[] = [
  { rule_name: "test_rule", passed: true, reason: "Test passed" },
];

const validCandidate: CandidateResult = {
  item_id: "item3",
  is_pairwise_compatible: true,
  cluster_if_added: {
    item_ids: ["item1", "item2", "item3"],
    is_valid: true,
    rule_evaluations: mockRuleEvaluations,
  },
};

const invalidCandidate: CandidateResult = {
  item_id: "item4",
  is_pairwise_compatible: true,
  cluster_if_added: {
    item_ids: ["item1", "item2", "item4"],
    is_valid: false,
    rule_evaluations: [
      { rule_name: "test_rule", passed: false, reason: "Test failed" },
    ],
  },
};

const incompatibleCandidate: CandidateResult = {
  item_id: "item5",
  is_pairwise_compatible: false,
  cluster_if_added: {
    item_ids: ["item1", "item2", "item5"],
    is_valid: false,
    rule_evaluations: [
      {
        rule_name: "pairwise_rule",
        passed: false,
        reason: "Pairwise incompatible",
      },
    ],
  },
};

const mockMatrix: EvaluationMatrix = {
  catalog_name: "test_catalog",
  ruleset_name: "test_ruleset",
  results: [
    {
      item1_id: "item1",
      item2_id: "item2",
      compatible: true,
      rules_evaluated: mockRuleEvaluations,
      evaluated_at: new Date().toISOString(),
    },
    {
      item1_id: "item1",
      item2_id: "item3",
      compatible: true,
      rules_evaluated: mockRuleEvaluations,
      evaluated_at: new Date().toISOString(),
    },
    {
      item1_id: "item2",
      item2_id: "item3",
      compatible: true,
      rules_evaluated: mockRuleEvaluations,
      evaluated_at: new Date().toISOString(),
    },
    {
      item1_id: "item1",
      item2_id: "item4",
      compatible: false,
      rules_evaluated: [
        { rule_name: "test_rule", passed: false, reason: "Incompatible" },
      ],
      evaluated_at: new Date().toISOString(),
    },
  ],
  total_comparisons: 4,
  compatible_count: 3,
  compatibility_rate: 0.75,
};

describe("filterVisibleItems", () => {
  it("should always include cluster items", () => {
    const result = filterVisibleItems(["item1", "item2"], [], [], [], false);
    expect(result).toContain("item1");
    expect(result).toContain("item2");
  });

  it("should include valid candidates", () => {
    const result = filterVisibleItems(
      ["item1"],
      [validCandidate],
      [],
      [],
      false,
    );
    expect(result).toContain("item1");
    expect(result).toContain("item3");
  });

  it("should include invalid candidates", () => {
    const result = filterVisibleItems(
      ["item1"],
      [],
      [invalidCandidate],
      [],
      false,
    );
    expect(result).toContain("item1");
    expect(result).toContain("item4");
  });

  it("should exclude incompatible candidates when toggle is off", () => {
    const result = filterVisibleItems(
      ["item1"],
      [],
      [],
      [incompatibleCandidate],
      false,
    );
    expect(result).not.toContain("item5");
  });

  it("should include incompatible candidates when toggle is on", () => {
    const result = filterVisibleItems(
      ["item1"],
      [],
      [],
      [incompatibleCandidate],
      true,
    );
    expect(result).toContain("item5");
  });

  it("should handle mixed candidates correctly", () => {
    const result = filterVisibleItems(
      ["item1", "item2"],
      [validCandidate],
      [invalidCandidate],
      [incompatibleCandidate],
      true,
    );
    expect(result).toContain("item1");
    expect(result).toContain("item2");
    expect(result).toContain("item3");
    expect(result).toContain("item4");
    expect(result).toContain("item5");
  });

  it("should not contain duplicates", () => {
    const result = filterVisibleItems(
      ["item1", "item1"], // duplicate cluster item
      [validCandidate],
      [],
      [],
      false,
    );
    const uniqueItems = new Set(result);
    expect(uniqueItems.size).toBe(result.length);
  });
});

describe("buildEdgesFromMatrix", () => {
  it("should build edges from matrix for visible items", () => {
    const edges = buildEdgesFromMatrix(
      mockMatrix,
      ["item1", "item2", "item3"],
      false,
    );
    expect(edges.length).toBeGreaterThan(0);
  });

  it("should only include edges between visible items", () => {
    const edges = buildEdgesFromMatrix(mockMatrix, ["item1", "item2"], false);
    const hasItem3Edge = edges.some(
      (e) => e.data.source === "item3" || e.data.target === "item3",
    );
    expect(hasItem3Edge).toBe(false);
  });

  it("should exclude incompatible edges when toggle is off", () => {
    const edges = buildEdgesFromMatrix(
      mockMatrix,
      ["item1", "item2", "item3", "item4"],
      false,
    );
    const incompatibleEdges = edges.filter((e) => !e.data.compatible);
    expect(incompatibleEdges.length).toBe(0);
  });

  it("should include incompatible edges when toggle is on", () => {
    const edges = buildEdgesFromMatrix(
      mockMatrix,
      ["item1", "item2", "item3", "item4"],
      true,
    );
    const incompatibleEdges = edges.filter((e) => !e.data.compatible);
    expect(incompatibleEdges.length).toBeGreaterThan(0);
  });

  it("should set correct edge properties for compatible edges", () => {
    const edges = buildEdgesFromMatrix(mockMatrix, ["item1", "item2"], false);
    const compatibleEdge = edges.find((e) => e.data.compatible);
    expect(compatibleEdge).toBeDefined();
    expect(compatibleEdge?.data.lineColor).toBe("#10b981");
    expect(compatibleEdge?.data.lineStyle).toBe("solid");
    expect(compatibleEdge?.classes).toBe("compatible");
  });

  it("should set correct edge properties for incompatible edges", () => {
    const edges = buildEdgesFromMatrix(mockMatrix, ["item1", "item4"], true);
    const incompatibleEdge = edges.find((e) => !e.data.compatible);
    expect(incompatibleEdge).toBeDefined();
    expect(incompatibleEdge?.data.lineColor).toBe("#f43f5e");
    expect(incompatibleEdge?.data.lineStyle).toBe("dashed");
    expect(incompatibleEdge?.classes).toBe("incompatible");
  });

  it("should handle null matrix", () => {
    const edges = buildEdgesFromMatrix(null, ["item1", "item2"], false);
    expect(edges).toEqual([]);
  });

  it("should handle empty visible items", () => {
    const edges = buildEdgesFromMatrix(mockMatrix, [], false);
    expect(edges).toEqual([]);
  });
});

describe("transformToGraphData", () => {
  it("should transform items and candidates into graph data", () => {
    const graphData = transformToGraphData(
      mockItems,
      mockMatrix,
      ["item1", "item2"],
      [validCandidate, invalidCandidate],
      false,
    );
    expect(graphData.nodes.length).toBeGreaterThan(0);
    expect(graphData.edges.length).toBeGreaterThan(0);
  });

  it("should categorize cluster nodes correctly", () => {
    const graphData = transformToGraphData(
      mockItems,
      mockMatrix,
      ["item1", "item2"],
      [],
      false,
    );
    const clusterNodes = graphData.nodes.filter(
      (n) => n.data.category === "cluster",
    );
    expect(clusterNodes.length).toBe(2);
    expect(clusterNodes[0].classes).toBe("cluster");
  });

  it("should categorize valid candidates correctly", () => {
    const graphData = transformToGraphData(
      mockItems,
      mockMatrix,
      ["item1"],
      [validCandidate],
      false,
    );
    const validNodes = graphData.nodes.filter(
      (n) => n.data.category === "valid",
    );
    expect(validNodes.length).toBeGreaterThan(0);
    expect(validNodes[0].data.backgroundColor).toBe("#10b981");
  });

  it("should categorize invalid candidates correctly", () => {
    const graphData = transformToGraphData(
      mockItems,
      mockMatrix,
      ["item1"],
      [invalidCandidate],
      false,
    );
    const invalidNodes = graphData.nodes.filter(
      (n) => n.data.category === "invalid",
    );
    expect(invalidNodes.length).toBeGreaterThan(0);
    expect(invalidNodes[0].data.backgroundColor).toBe("#f59e0b");
  });

  it("should categorize incompatible candidates correctly when shown", () => {
    const graphData = transformToGraphData(
      mockItems.concat([
        {
          item_id: "item5",
          name: "Item Five",
          attributes: {},
        },
      ]),
      mockMatrix,
      ["item1"],
      [incompatibleCandidate],
      true,
    );
    const incompatibleNodes = graphData.nodes.filter(
      (n) => n.data.category === "incompatible",
    );
    expect(incompatibleNodes.length).toBeGreaterThan(0);
    expect(incompatibleNodes[0].data.backgroundColor).toBe("#f43f5e");
  });

  it("should use item names as node labels", () => {
    const graphData = transformToGraphData(
      mockItems,
      mockMatrix,
      ["item1"],
      [],
      false,
    );
    const item1Node = graphData.nodes.find((n) => n.data.id === "item1");
    expect(item1Node?.data.label).toBe("Item One");
  });

  it("should handle null candidates", () => {
    const graphData = transformToGraphData(
      mockItems,
      mockMatrix,
      ["item1", "item2"],
      null,
      false,
    );
    expect(graphData.nodes.length).toBe(2);
  });

  it("should handle empty cluster", () => {
    const graphData = transformToGraphData(
      mockItems,
      mockMatrix,
      [],
      [validCandidate],
      false,
    );
    expect(graphData.nodes.length).toBeGreaterThan(0);
    const clusterNodes = graphData.nodes.filter(
      (n) => n.data.category === "cluster",
    );
    expect(clusterNodes.length).toBe(0);
  });

  it("should handle null matrix", () => {
    const graphData = transformToGraphData(
      mockItems,
      null,
      ["item1", "item2"],
      [validCandidate],
      false,
    );
    expect(graphData.nodes.length).toBeGreaterThan(0);
    expect(graphData.edges.length).toBe(0);
  });
});

describe("getItemName", () => {
  it("should return item name when item exists", () => {
    const name = getItemName("item1", mockItems);
    expect(name).toBe("Item One");
  });

  it("should return item ID when item not found", () => {
    const name = getItemName("nonexistent", mockItems);
    expect(name).toBe("nonexistent");
  });

  it("should handle empty items array", () => {
    const name = getItemName("item1", []);
    expect(name).toBe("item1");
  });
});
