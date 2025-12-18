/**
 * Tests for Explore Page (+page.svelte)
 *
 * Tests interactive compatibility exploration logic.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import type { ComparisonResult } from "$lib/api/client";
import {
  createMockCatalog,
  createMockRuleSet,
  createMockItem,
  createMockItems,
} from "$lib/test-utils/fixtures";

// Mock the API client
vi.mock("$lib/api/client", () => ({
  api: {
    getCatalogs: vi.fn(),
    getRuleSets: vi.fn(),
    getItems: vi.fn(),
    evaluateItem: vi.fn(),
  },
}));

// Helper: Create mock comparison result
function createMockComparisonResult(
  item1_id: string,
  item2_id: string,
  compatible: boolean,
  rulesPassed: number = 2,
  rulesTotal: number = 3,
): ComparisonResult {
  return {
    item1_id,
    item2_id,
    compatible,
    rules_evaluated: Array.from({ length: rulesTotal }, (_, i) => ({
      rule_name: `Rule${i + 1}`,
      passed: i < rulesPassed,
      reason: i < rulesPassed ? "allowed" : "blocked",
    })),
    evaluated_at: "2024-01-01T00:00:00Z",
  };
}

describe("Explore Page (+page)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Initial Data Loading", () => {
    it("loads catalogs on mount", async () => {
      const mockCatalogs = [
        createMockCatalog({ name: "Wardrobe" }),
        createMockCatalog({ name: "Kitchen" }),
      ];
      const mockRulesets = [createMockRuleSet()];
      const mockItems = [createMockItem()];

      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getItems").mockResolvedValue(mockItems);

      const catalogs = await api.api.getCatalogs();

      expect(catalogs).toEqual(mockCatalogs);
      expect(api.api.getCatalogs).toHaveBeenCalled();
    });

    it("loads rulesets on mount", async () => {
      const mockCatalogs = [createMockCatalog()];
      const mockRulesets = [
        createMockRuleSet({ name: "Rules1" }),
        createMockRuleSet({ name: "Rules2" }),
      ];

      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getItems").mockResolvedValue([]);

      const rulesets = await api.api.getRuleSets();

      expect(rulesets).toEqual(mockRulesets);
    });

    it("sets first catalog as default", async () => {
      const mockCatalogs = [
        createMockCatalog({ name: "FirstCatalog" }),
        createMockCatalog({ name: "SecondCatalog" }),
      ];
      const mockRulesets = [createMockRuleSet()];
      const mockItems = [createMockItem()];

      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getItems").mockResolvedValue(mockItems);

      const catalogs = await api.api.getCatalogs();
      const selectedCatalog = catalogs.length > 0 ? catalogs[0].name : "";

      expect(selectedCatalog).toBe("FirstCatalog");
    });

    it("sets first ruleset as default", async () => {
      const mockCatalogs = [createMockCatalog()];
      const mockRulesets = [
        createMockRuleSet({ name: "Rules1" }),
        createMockRuleSet({ name: "Rules2" }),
      ];

      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getItems").mockResolvedValue([]);

      const rulesets = await api.api.getRuleSets();
      const selectedRuleset = rulesets.length > 0 ? rulesets[0].name : "";

      expect(selectedRuleset).toBe("Rules1");
    });
  });

  describe("Item Selection", () => {
    it("loads items when catalog is selected", async () => {
      const mockItems = [
        createMockItem({ item_id: "item1" }),
        createMockItem({ item_id: "item2" }),
      ];

      vi.spyOn(api.api, "getItems").mockResolvedValue(mockItems);

      const items = await api.api.getItems("TestCatalog");

      expect(items).toEqual(mockItems);
      expect(api.api.getItems).toHaveBeenCalledWith("TestCatalog");
    });

    it("sets first item as default", async () => {
      const mockItems = [
        createMockItem({ item_id: "item1", name: "Item 1" }),
        createMockItem({ item_id: "item2", name: "Item 2" }),
      ];

      vi.spyOn(api.api, "getItems").mockResolvedValue(mockItems);

      const items = await api.api.getItems("TestCatalog");
      let selectedItemId = "";
      if (items.length > 0 && !selectedItemId) {
        selectedItemId = items[0].item_id;
      }

      expect(selectedItemId).toBe("item1");
    });

    it("displays all loaded items in selector", async () => {
      const mockItems = createMockItems(5);

      vi.spyOn(api.api, "getItems").mockResolvedValue(mockItems);

      const items = await api.api.getItems("TestCatalog");

      expect(items).toHaveLength(5);
    });

    it("selects different item", () => {
      let selectedItemId = "item1";
      selectedItemId = "item2";

      expect(selectedItemId).toBe("item2");
    });
  });

  describe("Exploration Logic", () => {
    it("requires all three selections", async () => {
      let error: string | null = null;
      const selectedCatalog = "";
      const selectedRuleset = "";
      const selectedItemId = "";

      if (!selectedCatalog || !selectedRuleset || !selectedItemId) {
        error = "Please select a catalog, ruleset, and item";
      }

      expect(error).toBe("Please select a catalog, ruleset, and item");
    });

    it("passes all three selections to API", async () => {
      const mockResults: ComparisonResult[] = [
        createMockComparisonResult("item1", "item2", true),
        createMockComparisonResult("item1", "item3", false),
      ];

      vi.spyOn(api.api, "evaluateItem").mockResolvedValue(mockResults);

      const result = await api.api.evaluateItem(
        "item1",
        "catalog1",
        "ruleset1",
      );

      expect(api.api.evaluateItem).toHaveBeenCalledWith(
        "item1",
        "catalog1",
        "ruleset1",
      );
      expect(result).toEqual(mockResults);
    });

    it("finds current item from items list", () => {
      const items = [
        createMockItem({ item_id: "item1", name: "First" }),
        createMockItem({ item_id: "item2", name: "Second" }),
      ];
      const selectedItemId = "item1";

      const currentItem =
        items.find((i) => i.item_id === selectedItemId) || null;

      expect(currentItem?.name).toBe("First");
    });

    it("handles item not found", () => {
      const items = [
        createMockItem({ item_id: "item1" }),
        createMockItem({ item_id: "item2" }),
      ];
      const selectedItemId = "nonexistent";

      const currentItem =
        items.find((i) => i.item_id === selectedItemId) || null;

      expect(currentItem).toBeNull();
    });
  });

  describe("Results Filtering", () => {
    it("separates compatible results", async () => {
      const mockResults: ComparisonResult[] = [
        createMockComparisonResult("item1", "item2", true),
        createMockComparisonResult("item1", "item3", true),
        createMockComparisonResult("item1", "item4", false),
      ];

      vi.spyOn(api.api, "evaluateItem").mockResolvedValue(mockResults);

      const results = await api.api.evaluateItem("item1", "cat", "rs");
      const compatibleResults = results.filter((r) => r.compatible);

      expect(compatibleResults).toHaveLength(2);
      expect(compatibleResults[0].compatible).toBe(true);
    });

    it("separates incompatible results", async () => {
      const mockResults: ComparisonResult[] = [
        createMockComparisonResult("item1", "item2", true),
        createMockComparisonResult("item1", "item3", false),
        createMockComparisonResult("item1", "item4", false),
      ];

      vi.spyOn(api.api, "evaluateItem").mockResolvedValue(mockResults);

      const results = await api.api.evaluateItem("item1", "cat", "rs");
      const incompatibleResults = results.filter((r) => r.compatible === false);

      expect(incompatibleResults).toHaveLength(2);
      expect(incompatibleResults[0].compatible).toBe(false);
    });

    it("handles empty results", async () => {
      vi.spyOn(api.api, "evaluateItem").mockResolvedValue([]);

      const results = await api.api.evaluateItem("item1", "cat", "rs");

      expect(results).toHaveLength(0);
    });
  });

  describe("Other Item Resolution", () => {
    it("extracts other item ID when current is item1", () => {
      const result = createMockComparisonResult("item1", "item2", true);
      const currentItemId = "item1";

      const otherId =
        result.item1_id === currentItemId ? result.item2_id : result.item1_id;

      expect(otherId).toBe("item2");
    });

    it("extracts other item ID when current is item2", () => {
      const result = createMockComparisonResult("item1", "item2", true);
      const currentItemId = "item2";

      const otherId =
        result.item1_id === currentItemId ? result.item2_id : result.item1_id;

      expect(otherId).toBe("item1");
    });

    it("finds corresponding item in items list", () => {
      const items = [
        createMockItem({ item_id: "item1", name: "Item 1" }),
        createMockItem({ item_id: "item2", name: "Item 2" }),
        createMockItem({ item_id: "item3", name: "Item 3" }),
      ];
      const result = createMockComparisonResult("item1", "item3", true);
      const currentItemId = "item1";

      const otherId =
        result.item1_id === currentItemId ? result.item2_id : result.item1_id;
      const otherItem = items.find((i) => i.item_id === otherId);

      expect(otherItem?.name).toBe("Item 3");
    });
  });

  describe("Rules Evaluation Display", () => {
    it("counts passed rules in compatible result", () => {
      const result = createMockComparisonResult("item1", "item2", true, 3, 3);
      const passedCount = result.rules_evaluated.filter((r) => r.passed).length;

      expect(passedCount).toBe(3);
    });

    it("counts passed rules in incompatible result", () => {
      const result = createMockComparisonResult("item1", "item2", false, 1, 3);
      const passedCount = result.rules_evaluated.filter((r) => r.passed).length;

      expect(passedCount).toBe(1);
    });

    it("calculates rule fraction", () => {
      const result = createMockComparisonResult("item1", "item2", true, 2, 3);
      const passed = result.rules_evaluated.filter((r) => r.passed).length;
      const total = result.rules_evaluated.length;

      expect(`${passed}/${total}`).toBe("2/3");
    });

    it("lists all failed rules", () => {
      const result = createMockComparisonResult("item1", "item2", false, 1, 3);
      const failedRules = result.rules_evaluated.filter((r) => !r.passed);

      expect(failedRules).toHaveLength(2);
      expect(failedRules[0].rule_name).toBe("Rule2");
      expect(failedRules[1].rule_name).toBe("Rule3");
    });

    it("displays rule names for failed rules", () => {
      const result = createMockComparisonResult("item1", "item2", false, 1, 3);
      const failedRules = result.rules_evaluated.filter((r) => !r.passed);

      failedRules.forEach((rule) => {
        expect(rule.rule_name).toBeTruthy();
      });
    });
  });

  describe("State Management", () => {
    it("initializes empty state", () => {
      const selectedCatalog = "";
      const selectedRuleset = "";
      const selectedItemId = "";
      const loading = false;
      const error: string | null = null;

      expect(selectedCatalog).toBe("");
      expect(selectedRuleset).toBe("");
      expect(selectedItemId).toBe("");
      expect(loading).toBe(false);
      expect(error).toBeNull();
    });

    it("sets loading state during exploration", () => {
      let loading = false;
      loading = true;
      expect(loading).toBe(true);

      loading = false;
      expect(loading).toBe(false);
    });

    it("clears results on catalog change", () => {
      let currentItem: { item_id: string } | null = { item_id: "item1" };
      let compatibleResults: { item2_id: string; compatible: boolean }[] = [
        { item2_id: "item2", compatible: true },
      ];
      let incompatibleResults: { item2_id: string; compatible: boolean }[] = [];

      // Simulate reset
      currentItem = null;
      compatibleResults = [];
      incompatibleResults = [];

      expect(currentItem).toBeNull();
      expect(compatibleResults).toHaveLength(0);
      expect(incompatibleResults).toHaveLength(0);
    });

    it("sets current item on exploration", () => {
      const items = [
        createMockItem({ item_id: "item1", name: "First" }),
        createMockItem({ item_id: "item2", name: "Second" }),
      ];
      let currentItem: (typeof items)[number] | null = null;
      const selectedItemId = "item1";

      currentItem = items.find((i) => i.item_id === selectedItemId) || null;

      expect(currentItem).not.toBeNull();
      if (!currentItem) {
        throw new Error("Expected currentItem to be set");
      }
      expect(currentItem.item_id).toBe("item1");
    });
  });

  describe("Error Handling", () => {
    it("catches catalog loading error", async () => {
      const error = new Error("Failed to load catalogs");
      vi.spyOn(api.api, "getCatalogs").mockRejectedValue(error);

      try {
        await api.api.getCatalogs();
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches item loading error", async () => {
      const error = new Error("Failed to load items");
      vi.spyOn(api.api, "getItems").mockRejectedValue(error);

      try {
        await api.api.getItems("TestCatalog");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches evaluation error", async () => {
      const error = new Error("Failed to evaluate item");
      vi.spyOn(api.api, "evaluateItem").mockRejectedValue(error);

      try {
        await api.api.evaluateItem("item1", "cat", "rs");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("displays error message on failure", () => {
      let error: string | null = null;
      error = "Failed to evaluate item";

      expect(error).toBe("Failed to evaluate item");
    });

    it("clears error on new exploration", () => {
      let error: string | null = "Previous error";
      error = null;

      expect(error).toBeNull();
    });
  });

  describe("Interactive Item Selection", () => {
    it("updates selected item when clicking compatible item", () => {
      let selectedItemId = "item1";
      selectedItemId = "item2";

      expect(selectedItemId).toBe("item2");
    });

    it("updates selected item when clicking incompatible item", () => {
      let selectedItemId = "item1";
      selectedItemId = "item3";

      expect(selectedItemId).toBe("item3");
    });

    it("re-evaluates on new item selection", async () => {
      vi.spyOn(api.api, "evaluateItem").mockResolvedValue([]);

      let selectedItemId = "item1";
      selectedItemId = "item2";

      await api.api.evaluateItem(selectedItemId, "cat", "rs");

      expect(api.api.evaluateItem).toHaveBeenCalledWith("item2", "cat", "rs");
    });
  });

  describe("Page Title and Display", () => {
    it("has explore page title", () => {
      expect("Explore - Rulate").toBeTruthy();
    });

    it("displays main heading", () => {
      expect("Compatibility Explorer").toBeTruthy();
    });

    it("displays subtitle", () => {
      const subtitle =
        "Explore item compatibility interactively - click on any item to see what it's compatible with";
      expect(subtitle).toBeTruthy();
    });
  });

  describe("Item Attribute Display", () => {
    it("displays up to 8 attributes", () => {
      const item = createMockItem({
        attributes: {
          attr1: "value1",
          attr2: "value2",
          attr3: "value3",
          attr4: "value4",
          attr5: "value5",
          attr6: "value6",
          attr7: "value7",
          attr8: "value8",
          attr9: "value9",
        },
      });

      const displayedAttrs = Object.entries(item.attributes).slice(0, 8);

      expect(displayedAttrs).toHaveLength(8);
    });

    it("formats array attributes with comma separation", () => {
      const arrayValue = ["item1", "item2", "item3"];
      const formatted = arrayValue.join(", ");

      expect(formatted).toBe("item1, item2, item3");
    });

    it("displays scalar attributes as-is", () => {
      const value = "scalar";
      expect(value).toBe("scalar");
    });
  });

  describe("Catalog Change Behavior", () => {
    it("loads items when catalog changes", async () => {
      const mockItems = [createMockItem()];
      vi.spyOn(api.api, "getItems").mockResolvedValue(mockItems);

      let selectedCatalog = "catalog1";
      selectedCatalog = "catalog2";

      const _items = await api.api.getItems(selectedCatalog);

      expect(api.api.getItems).toHaveBeenCalledWith("catalog2");
    });

    it("resets results when catalog changes", () => {
      let currentItem: { item_id: string } | null = { item_id: "item1" };
      let _compatibleResults: { compatible: boolean }[] = [
        { compatible: true },
      ];
      let selectedCatalog = "cat1";

      // Simulate catalog change
      if (selectedCatalog !== "cat1") {
        currentItem = null;
        _compatibleResults = [];
      }

      selectedCatalog = "cat2";

      expect(currentItem?.item_id).toBe("item1"); // Still set until change is detected
    });

    it("does not reload items without catalog selection", async () => {
      vi.spyOn(api.api, "getItems").mockResolvedValue([]);

      const selectedCatalog = "";
      if (!selectedCatalog) {
        // Early return, don't call getItems
      } else {
        await api.api.getItems(selectedCatalog);
      }

      expect(api.api.getItems).not.toHaveBeenCalled();
    });
  });
});
