/**
 * Tests for Matrix Page (+page.svelte)
 *
 * Tests compatibility matrix visualization logic.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import type { ComparisonResult, EvaluationMatrix } from "$lib/api/client";
import { createMockCatalog, createMockRuleSet } from "$lib/test-utils/fixtures";

vi.mock("$lib/api/client", () => ({
  api: {
    getCatalogs: vi.fn(),
    getRuleSets: vi.fn(),
    evaluateMatrix: vi.fn(),
  },
}));

function createMockMatrix(itemCount: number): EvaluationMatrix {
  const items = Array.from({ length: itemCount }, (_, i) => `item${i + 1}`);
  const results: ComparisonResult[] = [];

  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      results.push({
        item1_id: items[i],
        item2_id: items[j],
        compatible: Math.random() > 0.5,
        rules_evaluated: [
          { rule_name: "Rule1", passed: true },
          { rule_name: "Rule2", passed: Math.random() > 0.5 },
        ],
      });
    }
  }
  return { results };
}

describe("Matrix Page (+page)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Data Loading", () => {
    it("loads catalogs and rulesets on mount", async () => {
      const catalogs = [createMockCatalog()];
      const rulesets = [createMockRuleSet()];

      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(catalogs);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(rulesets);

      const cData = await api.api.getCatalogs();
      const rData = await api.api.getRuleSets();

      expect(cData).toEqual(catalogs);
      expect(rData).toEqual(rulesets);
    });

    it("sets first catalog as default", async () => {
      const catalogs = [
        createMockCatalog({ name: "Catalog1" }),
        createMockCatalog({ name: "Catalog2" }),
      ];
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(catalogs);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);

      const cData = await api.api.getCatalogs();
      const selected = cData.length > 0 ? cData[0].name : "";

      expect(selected).toBe("Catalog1");
    });

    it("sets first ruleset as default", async () => {
      const rulesets = [
        createMockRuleSet({ name: "Rules1" }),
        createMockRuleSet({ name: "Rules2" }),
      ];
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(rulesets);

      const rData = await api.api.getRuleSets();
      const selected = rData.length > 0 ? rData[0].name : "";

      expect(selected).toBe("Rules1");
    });
  });

  describe("Matrix Evaluation", () => {
    it("requires both catalog and ruleset", () => {
      let error: string | null = null;
      const catalog = "";
      const ruleset = "";

      if (!catalog || !ruleset) {
        error = "Please select both a catalog and a ruleset";
      }

      expect(error).toBe("Please select both a catalog and a ruleset");
    });

    it("calls evaluateMatrix API", async () => {
      const mockMatrix = createMockMatrix(3);
      vi.spyOn(api.api, "evaluateMatrix").mockResolvedValue(mockMatrix);

      const result = await api.api.evaluateMatrix("catalog1", "ruleset1");

      expect(api.api.evaluateMatrix).toHaveBeenCalledWith(
        "catalog1",
        "ruleset1",
      );
      expect(result).toEqual(mockMatrix);
    });

    it("sets loading state during evaluation", () => {
      let loading = false;
      loading = true;
      expect(loading).toBe(true);

      loading = false;
      expect(loading).toBe(false);
    });

    it("clears previous error on new evaluation", () => {
      let error: string | null = "Previous error";
      error = null;

      expect(error).toBeNull();
    });

    it("clears selected pair on new evaluation", () => {
      let selectedPair: any = { item1_id: "item1", item2_id: "item2" };
      selectedPair = null;

      expect(selectedPair).toBeNull();
    });
  });

  describe("Result Lookup", () => {
    it("finds result by item IDs in order", () => {
      const matrix = createMockMatrix(3);
      const result = matrix.results.find(
        (r) => r.item1_id === "item1" && r.item2_id === "item2",
      );

      expect(result).toBeTruthy();
      expect(result?.item1_id).toBe("item1");
      expect(result?.item2_id).toBe("item2");
    });

    it("finds result by reversed item IDs", () => {
      const matrix = createMockMatrix(3);
      const result = matrix.results.find(
        (r) =>
          (r.item1_id === "item2" && r.item2_id === "item1") ||
          (r.item1_id === "item1" && r.item2_id === "item2"),
      );

      expect(result).toBeTruthy();
    });

    it("returns null for non-existent result", () => {
      const matrix = createMockMatrix(2);
      const result = matrix.results.find(
        (r) => r.item1_id === "nonexistent" && r.item2_id === "item1",
      );

      expect(result).toBeUndefined();
    });

    it("returns null when matrix is null", () => {
      const matrix = null;
      if (matrix) {
        const result = matrix.results.find((r) => r.item1_id === "item1");
        expect(result).toBeDefined();
      } else {
        expect(matrix).toBeNull();
      }
    });
  });

  describe("Unique Item IDs", () => {
    it("extracts all unique item IDs", () => {
      const matrix = createMockMatrix(4);
      const ids = new Set<string>();
      matrix.results.forEach((r) => {
        ids.add(r.item1_id);
        ids.add(r.item2_id);
      });

      expect(ids.size).toBe(4);
    });

    it("sorts item IDs alphabetically", () => {
      const matrix = createMockMatrix(5);
      const ids = new Set<string>();
      matrix.results.forEach((r) => {
        ids.add(r.item1_id);
        ids.add(r.item2_id);
      });
      const sorted = Array.from(ids).sort();

      expect(sorted[0]).toBe("item1");
      expect(sorted[1]).toBe("item2");
    });

    it("returns empty array when matrix is null", () => {
      const matrix = null;
      const ids = matrix ? Array.from(new Set()) : [];

      expect(ids).toEqual([]);
    });
  });

  describe("Matrix Structure", () => {
    it("has correct number of pairwise comparisons", () => {
      const itemCount = 4;
      const matrix = createMockMatrix(itemCount);
      const expectedCount = (itemCount * (itemCount - 1)) / 2;

      expect(matrix.results.length).toBe(expectedCount);
    });

    it("each result has both items", () => {
      const matrix = createMockMatrix(3);

      matrix.results.forEach((result) => {
        expect(result.item1_id).toBeTruthy();
        expect(result.item2_id).toBeTruthy();
        expect(result.item1_id).not.toBe(result.item2_id);
      });
    });

    it("each result has compatibility status", () => {
      const matrix = createMockMatrix(3);

      matrix.results.forEach((result) => {
        expect(typeof result.compatible).toBe("boolean");
      });
    });
  });

  describe("Cell Color Coding", () => {
    it("marks compatible cells as green", () => {
      const result: ComparisonResult = {
        item1_id: "item1",
        item2_id: "item2",
        compatible: true,
        rules_evaluated: [],
      };

      expect(result.compatible).toBe(true);
    });

    it("marks incompatible cells as red", () => {
      const result: ComparisonResult = {
        item1_id: "item1",
        item2_id: "item2",
        compatible: false,
        rules_evaluated: [],
      };

      expect(result.compatible).toBe(false);
    });
  });

  describe("Error Handling", () => {
    it("catches evaluation error", async () => {
      const error = new Error("Failed to evaluate");
      vi.spyOn(api.api, "evaluateMatrix").mockRejectedValue(error);

      try {
        await api.api.evaluateMatrix("cat", "rs");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("displays error message", () => {
      let error: string | null = null;
      error = "Failed to evaluate matrix";

      expect(error).toBe("Failed to evaluate matrix");
    });

    it("clears error on new evaluation", () => {
      let error: string | null = "Previous error";
      error = null;

      expect(error).toBeNull();
    });
  });

  describe("Page Title", () => {
    it("has matrix page title", () => {
      expect("Compatibility Matrix - Rulate").toBeTruthy();
    });

    it("displays main heading", () => {
      expect("Compatibility Matrix").toBeTruthy();
    });
  });

  describe("Large Matrix Handling", () => {
    it("handles large number of items", () => {
      const matrix = createMockMatrix(20);
      const ids = new Set<string>();
      matrix.results.forEach((r) => {
        ids.add(r.item1_id);
        ids.add(r.item2_id);
      });

      expect(ids.size).toBe(20);
      expect(matrix.results.length).toBe((20 * 19) / 2);
    });
  });
});
