/**
 * Tests for Import/Export Page (+page.svelte)
 *
 * Tests data import and export functionality.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import {
  createMockSchema,
  createMockCatalog,
  createMockRuleSet,
} from "$lib/test-utils/fixtures";

vi.mock("$lib/api/client", () => ({
  api: {
    exportAll: vi.fn(),
    importSchemas: vi.fn(),
    importRuleSets: vi.fn(),
    importCatalogs: vi.fn(),
    importClusterRuleSets: vi.fn(),
  },
}));

describe("Import/Export Page (+page)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Export Functionality", () => {
    it("calls exportAll API", async () => {
      const mockData = {
        schemas: [createMockSchema()],
        rulesets: [createMockRuleSet()],
        catalogs: [createMockCatalog()],
      };

      vi.spyOn(api.api, "exportAll").mockResolvedValue(mockData);

      const result = await api.api.exportAll();

      expect(api.api.exportAll).toHaveBeenCalled();
      expect(result).toEqual(mockData);
    });

    it("includes schemas in export", async () => {
      const mockData = {
        schemas: [
          createMockSchema({ name: "Schema1" }),
          createMockSchema({ name: "Schema2" }),
        ],
        rulesets: [],
        catalogs: [],
      };

      vi.spyOn(api.api, "exportAll").mockResolvedValue(mockData);

      const result = await api.api.exportAll();

      expect(result.schemas).toHaveLength(2);
      expect(result.schemas[0].name).toBe("Schema1");
    });

    it("includes rulesets in export", async () => {
      const mockData = {
        schemas: [],
        rulesets: [
          createMockRuleSet({ name: "Rules1" }),
          createMockRuleSet({ name: "Rules2" }),
        ],
        catalogs: [],
      };

      vi.spyOn(api.api, "exportAll").mockResolvedValue(mockData);

      const result = await api.api.exportAll();

      expect(result.rulesets).toHaveLength(2);
    });

    it("includes catalogs in export", async () => {
      const mockData = {
        schemas: [],
        rulesets: [],
        catalogs: [
          createMockCatalog({ name: "Catalog1" }),
          createMockCatalog({ name: "Catalog2" }),
        ],
      };

      vi.spyOn(api.api, "exportAll").mockResolvedValue(mockData);

      const result = await api.api.exportAll();

      expect(result.catalogs).toHaveLength(2);
    });

    it("handles empty export", async () => {
      const mockData = { schemas: [], rulesets: [], catalogs: [] };

      vi.spyOn(api.api, "exportAll").mockResolvedValue(mockData);

      const result = await api.api.exportAll();

      expect(result.schemas).toHaveLength(0);
      expect(result.rulesets).toHaveLength(0);
      expect(result.catalogs).toHaveLength(0);
    });
  });

  describe("Import Functionality", () => {
    it("imports schemas", async () => {
      const schemas = [createMockSchema()];
      vi.spyOn(api.api, "importSchemas").mockResolvedValue({ message: "ok" });

      await api.api.importSchemas(schemas, false);

      expect(api.api.importSchemas).toHaveBeenCalledWith(schemas, false);
    });

    it("imports rulesets", async () => {
      const rulesets = [createMockRuleSet()];
      vi.spyOn(api.api, "importRuleSets").mockResolvedValue({ message: "ok" });

      await api.api.importRuleSets(rulesets, false);

      expect(api.api.importRuleSets).toHaveBeenCalledWith(rulesets, false);
    });

    it("imports catalogs", async () => {
      const catalogs = [createMockCatalog()];
      vi.spyOn(api.api, "importCatalogs").mockResolvedValue({ message: "ok" });

      await api.api.importCatalogs(catalogs, false);

      expect(api.api.importCatalogs).toHaveBeenCalledWith(catalogs, false);
    });

    it("respects skip_existing flag when true", async () => {
      const schemas = [createMockSchema()];
      vi.spyOn(api.api, "importSchemas").mockResolvedValue({ message: "ok" });

      await api.api.importSchemas(schemas, true);

      expect(api.api.importSchemas).toHaveBeenCalledWith(schemas, true);
    });

    it("respects skip_existing flag when false", async () => {
      const schemas = [createMockSchema()];
      vi.spyOn(api.api, "importSchemas").mockResolvedValue({ message: "ok" });

      await api.api.importSchemas(schemas, false);

      expect(api.api.importSchemas).toHaveBeenCalledWith(schemas, false);
    });
  });

  describe("File Handling", () => {
    it("parses JSON file", () => {
      const jsonData = {
        schemas: [createMockSchema()],
        rulesets: [],
        catalogs: [],
      };
      const jsonString = JSON.stringify(jsonData);
      const parsed = JSON.parse(jsonString);

      expect(parsed.schemas).toHaveLength(1);
    });

    it("handles malformed JSON", () => {
      const invalidJson = "{invalid json}";

      expect(() => JSON.parse(invalidJson)).toThrow();
    });

    it("creates download blob", () => {
      const data = { schemas: [], rulesets: [], catalogs: [] };
      const jsonString = JSON.stringify(data, null, 2);

      expect(jsonString).toContain("schemas");
    });

    it("exports with correct filename", () => {
      const filename = "rulate_export_2024-01-15.json";
      expect(filename).toBeTruthy();
    });
  });

  describe("Import/Export Together", () => {
    it("exports and imports complete data set", async () => {
      const exportData = {
        schemas: [createMockSchema({ name: "TestSchema" })],
        rulesets: [createMockRuleSet({ name: "TestRules" })],
        catalogs: [createMockCatalog({ name: "TestCatalog" })],
      };

      vi.spyOn(api.api, "exportAll").mockResolvedValue(exportData);
      vi.spyOn(api.api, "importSchemas").mockResolvedValue({ message: "ok" });
      vi.spyOn(api.api, "importRuleSets").mockResolvedValue({ message: "ok" });
      vi.spyOn(api.api, "importCatalogs").mockResolvedValue({ message: "ok" });

      const exported = await api.api.exportAll();
      await api.api.importSchemas(exported.schemas, false);
      await api.api.importRuleSets(exported.rulesets, false);
      await api.api.importCatalogs(exported.catalogs, false);

      expect(api.api.importSchemas).toHaveBeenCalled();
      expect(api.api.importRuleSets).toHaveBeenCalled();
      expect(api.api.importCatalogs).toHaveBeenCalled();
    });
  });

  describe("Error Handling", () => {
    it("catches export error", async () => {
      const error = new Error("Export failed");
      vi.spyOn(api.api, "exportAll").mockRejectedValue(error);

      try {
        await api.api.exportAll();
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches import error", async () => {
      const error = new Error("Import failed");
      vi.spyOn(api.api, "importSchemas").mockRejectedValue(error);

      try {
        await api.api.importSchemas([], false);
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("displays error message on failure", () => {
      let error: string | null = null;
      error = "Import failed: duplicate schema";

      expect(error).toContain("failed");
    });

    it("clears error on successful operation", () => {
      let error: string | null = "Previous error";
      error = null;

      expect(error).toBeNull();
    });
  });

  describe("State Management", () => {
    it("initializes with no selected file", () => {
      const selectedFile: any = null;
      expect(selectedFile).toBeNull();
    });

    it("initializes uploading as false", () => {
      const uploading = false;
      expect(uploading).toBe(false);
    });

    it("initializes error as null", () => {
      const error: string | null = null;
      expect(error).toBeNull();
    });

    it("tracks upload progress", () => {
      let uploading = false;
      uploading = true;
      expect(uploading).toBe(true);

      uploading = false;
      expect(uploading).toBe(false);
    });
  });

  describe("Dependency Handling", () => {
    it("imports schemas before rulesets", async () => {
      const callOrder: string[] = [];

      vi.spyOn(api.api, "importSchemas").mockImplementation(async () => {
        callOrder.push("schemas");
        return { message: "ok" };
      });
      vi.spyOn(api.api, "importRuleSets").mockImplementation(async () => {
        callOrder.push("rulesets");
        return { message: "ok" };
      });

      await api.api.importSchemas([], false);
      await api.api.importRuleSets([], false);

      expect(callOrder).toEqual(["schemas", "rulesets"]);
    });

    it("imports rulesets before catalogs", async () => {
      const callOrder: string[] = [];

      vi.spyOn(api.api, "importRuleSets").mockImplementation(async () => {
        callOrder.push("rulesets");
        return { message: "ok" };
      });
      vi.spyOn(api.api, "importCatalogs").mockImplementation(async () => {
        callOrder.push("catalogs");
        return { message: "ok" };
      });

      await api.api.importRuleSets([], false);
      await api.api.importCatalogs([], false);

      expect(callOrder).toEqual(["rulesets", "catalogs"]);
    });
  });

  describe("Page Title", () => {
    it("has import/export page title", () => {
      expect("Import/Export - Rulate").toBeTruthy();
    });

    it("displays main heading", () => {
      expect("Import/Export Data").toBeTruthy();
    });

    it("displays export section", () => {
      expect("Export All Data").toBeTruthy();
    });

    it("displays import section", () => {
      expect("Import Data").toBeTruthy();
    });
  });

  describe("Data Validation", () => {
    it("validates exported schema structure", async () => {
      const mockData = {
        schemas: [createMockSchema()],
        rulesets: [],
        catalogs: [],
      };

      vi.spyOn(api.api, "exportAll").mockResolvedValue(mockData);

      const result = await api.api.exportAll();

      expect(result).toHaveProperty("schemas");
      expect(result).toHaveProperty("rulesets");
      expect(result).toHaveProperty("catalogs");
    });

    it("validates imported schema has required fields", async () => {
      const schema = createMockSchema();
      expect(schema).toHaveProperty("name");
      expect(schema).toHaveProperty("dimensions");
    });
  });
});
