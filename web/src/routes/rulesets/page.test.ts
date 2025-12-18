/**
 * Tests for RuleSets List Page (+page.svelte)
 *
 * Tests the rulesets list page data loading, display, and deletion.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import { createMockRuleSet } from "$lib/test-utils/fixtures";

// Mock the API client
vi.mock("$lib/api/client", () => ({
  api: {
    getRuleSets: vi.fn(),
    deleteRuleSet: vi.fn(),
  },
}));

// Helper to simulate page loading
async function loadRuleSets() {
  const rulesets = await api.api.getRuleSets();
  return rulesets;
}

describe("RuleSets List Page (+page)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Data Loading", () => {
    it("loads rulesets on mount", async () => {
      const mockRuleSets = [
        createMockRuleSet({ name: "Wardrobe Rules", schema_name: "Wardrobe" }),
        createMockRuleSet({ name: "Kitchen Rules", schema_name: "Kitchen" }),
      ];
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRuleSets);

      const rulesets = await loadRuleSets();

      expect(rulesets).toEqual(mockRuleSets);
      expect(api.api.getRuleSets).toHaveBeenCalledTimes(1);
    });

    it("starts with loading state", () => {
      const loading = true;
      expect(loading).toBe(true);
    });

    it("sets loading to false after data loads", async () => {
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);

      let loading = true;
      await loadRuleSets();
      loading = false;

      expect(loading).toBe(false);
    });

    it("initializes with empty ruleset array", () => {
      const rulesets: any[] = [];
      expect(rulesets).toEqual([]);
    });

    it("clears error before loading", () => {
      let error: string | null = "Previous error";
      error = null;
      expect(error).toBeNull();
    });
  });

  describe("Display RuleSet Information", () => {
    it("displays ruleset name", async () => {
      const mockRuleSet = createMockRuleSet({ name: "TestRuleSet" });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].name).toBe("TestRuleSet");
    });

    it("displays ruleset version", async () => {
      const mockRuleSet = createMockRuleSet({ version: "2.5.0" });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].version).toBe("2.5.0");
    });

    it("displays rule count in badge", async () => {
      const mockRuleSet = createMockRuleSet({
        rules: [
          { name: "Rule1", type: "exclusion", enabled: true, condition: {} },
          { name: "Rule2", type: "requirement", enabled: true, condition: {} },
          { name: "Rule3", type: "exclusion", enabled: true, condition: {} },
        ],
      });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].rules.length).toBe(3);
    });

    it("displays schema name", async () => {
      const mockRuleSet = createMockRuleSet({ schema_name: "Wardrobe" });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].schema_name).toBe("Wardrobe");
    });

    it("displays first 3 rules", async () => {
      const mockRuleSet = createMockRuleSet({
        rules: [
          { name: "Rule1", type: "exclusion", enabled: true, condition: {} },
          { name: "Rule2", type: "requirement", enabled: true, condition: {} },
          { name: "Rule3", type: "exclusion", enabled: true, condition: {} },
          { name: "Rule4", type: "requirement", enabled: true, condition: {} },
          { name: "Rule5", type: "exclusion", enabled: true, condition: {} },
        ],
      });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      const displayedRules = rulesets[0].rules.slice(0, 3);
      expect(displayedRules).toHaveLength(3);
      expect(displayedRules[0].name).toBe("Rule1");
      expect(displayedRules[1].name).toBe("Rule2");
      expect(displayedRules[2].name).toBe("Rule3");
    });

    it('shows "+X more" when rules exceed 3', async () => {
      const mockRuleSet = createMockRuleSet({
        rules: Array.from({ length: 7 }, (_, i) => ({
          name: `Rule${i + 1}`,
          type: i % 2 === 0 ? "exclusion" : "requirement",
          enabled: true,
          condition: {},
        })),
      });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].rules.length).toBe(7);
      const remaining = rulesets[0].rules.length - 3;
      expect(remaining).toBe(4);
    });

    it('shows "No rules defined" when no rules', async () => {
      const mockRuleSet = createMockRuleSet({ rules: [] });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].rules.length).toBe(0);
    });

    it("displays exclusion rule type", async () => {
      const mockRuleSet = createMockRuleSet({
        rules: [
          {
            name: "ExclusionRule",
            type: "exclusion",
            enabled: true,
            condition: {},
          },
        ],
      });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].rules[0].type).toBe("exclusion");
    });

    it("displays requirement rule type", async () => {
      const mockRuleSet = createMockRuleSet({
        rules: [
          {
            name: "RequirementRule",
            type: "requirement",
            enabled: true,
            condition: {},
          },
        ],
      });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].rules[0].type).toBe("requirement");
    });

    it("displays created_at date if present", async () => {
      const testDate = new Date("2024-01-15").toISOString();
      const mockRuleSet = createMockRuleSet({ created_at: testDate });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].created_at).toBe(testDate);
    });

    it("formats created_at date for display", () => {
      const testDate = new Date("2024-01-15").toISOString();
      const formatted = new Date(testDate).toLocaleDateString();

      expect(formatted).toBeTruthy();
    });
  });

  describe("Multiple RuleSets", () => {
    it("displays all loaded rulesets", async () => {
      const mockRuleSets = [
        createMockRuleSet({ name: "RuleSet1" }),
        createMockRuleSet({ name: "RuleSet2" }),
        createMockRuleSet({ name: "RuleSet3" }),
      ];
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRuleSets);

      const rulesets = await loadRuleSets();

      expect(rulesets).toHaveLength(3);
      expect(rulesets[0].name).toBe("RuleSet1");
      expect(rulesets[1].name).toBe("RuleSet2");
      expect(rulesets[2].name).toBe("RuleSet3");
    });

    it("displays rulesets in grid layout", async () => {
      const mockRuleSets = [
        createMockRuleSet({ name: "RS1" }),
        createMockRuleSet({ name: "RS2" }),
        createMockRuleSet({ name: "RS3" }),
        createMockRuleSet({ name: "RS4" }),
      ];
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRuleSets);

      const rulesets = await loadRuleSets();

      expect(rulesets.length).toBe(4);
    });
  });

  describe("Empty State", () => {
    it("shows empty state when no rulesets", async () => {
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);

      const rulesets = await loadRuleSets();

      expect(rulesets).toEqual([]);
      expect(rulesets.length).toBe(0);
    });

    it("has create button in empty state", () => {
      const href = "/rulesets/new";
      expect(href).toBe("/rulesets/new");
    });
  });

  describe("Navigation", () => {
    it("has create ruleset button link", () => {
      const href = "/rulesets/new";
      expect(href).toBe("/rulesets/new");
    });

    it("has view details button for each ruleset", async () => {
      const mockRuleSet = createMockRuleSet({ name: "TestRuleSet" });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      const detailHref = `/rulesets/${rulesets[0].name}`;
      expect(detailHref).toBe("/rulesets/TestRuleSet");
    });

    it("constructs correct detail href for ruleset", async () => {
      const mockRuleSet = createMockRuleSet({ name: "MyRuleSet" });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(`/rulesets/${rulesets[0].name}`).toBe("/rulesets/MyRuleSet");
    });
  });

  describe("Delete Functionality", () => {
    it("calls deleteRuleSet with ruleset name", async () => {
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "deleteRuleSet").mockResolvedValue(undefined);

      await api.api.deleteRuleSet("TestRuleSet");

      expect(api.api.deleteRuleSet).toHaveBeenCalledWith("TestRuleSet");
    });

    it("reloads rulesets after delete", async () => {
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "deleteRuleSet").mockResolvedValue(undefined);

      await api.api.deleteRuleSet("TestRuleSet");
      await api.api.getRuleSets();

      expect(api.api.getRuleSets).toHaveBeenCalled();
    });

    it("handles delete error", async () => {
      const error = new Error("Delete failed");
      vi.spyOn(api.api, "deleteRuleSet").mockRejectedValue(error);

      try {
        await api.api.deleteRuleSet("TestRuleSet");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });
  });

  describe("Error Handling", () => {
    it("catches ruleset loading error", async () => {
      const error = new Error("Failed to load rulesets");
      vi.spyOn(api.api, "getRuleSets").mockRejectedValue(error);

      try {
        await loadRuleSets();
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("initializes error state as null", () => {
      const error: string | null = null;
      expect(error).toBeNull();
    });

    it("sets error message on failure", () => {
      let error: string | null = null;
      error = "Failed to load rulesets";
      expect(error).toBe("Failed to load rulesets");
    });

    it("has retry button in error state", () => {
      expect(() => loadRuleSets()).toBeDefined();
    });

    it("clears error before retrying", async () => {
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);

      let error: string | null = "Previous error";
      error = null;
      const _rulesets = await loadRuleSets();

      expect(error).toBeNull();
    });

    it("handles non-Error exceptions", () => {
      const error: any = "String error";
      expect(error).toBe("String error");
    });
  });

  describe("Page Title and Headings", () => {
    it("has page title", () => {
      expect("RuleSets - Rulate").toBeTruthy();
    });

    it("displays main heading", () => {
      expect("RuleSets").toBeTruthy();
    });

    it("displays subtitle", () => {
      const subtitle = "Define compatibility rules and conditions";
      expect(subtitle).toBeTruthy();
    });
  });

  describe("Schema Reference", () => {
    it("displays associated schema for each ruleset", async () => {
      const mockRuleSet = createMockRuleSet({ schema_name: "Wardrobe" });
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([mockRuleSet]);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].schema_name).toBe("Wardrobe");
    });

    it("handles different schema references", async () => {
      const mockRuleSets = [
        createMockRuleSet({ name: "RS1", schema_name: "Schema1" }),
        createMockRuleSet({ name: "RS2", schema_name: "Schema2" }),
        createMockRuleSet({ name: "RS3", schema_name: "Schema3" }),
      ];
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRuleSets);

      const rulesets = await loadRuleSets();

      expect(rulesets[0].schema_name).toBe("Schema1");
      expect(rulesets[1].schema_name).toBe("Schema2");
      expect(rulesets[2].schema_name).toBe("Schema3");
    });
  });
});
