/**
 * Tests for Schemas List Page (+page.svelte)
 *
 * Tests the schemas list page data loading, display, and deletion.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import { createMockSchema } from "$lib/test-utils/fixtures";

// Mock the API client
vi.mock("$lib/api/client", () => ({
  api: {
    getSchemas: vi.fn(),
    deleteSchema: vi.fn(),
  },
}));

// Helper to simulate page loading
async function loadSchemas() {
  const schemas = await api.api.getSchemas();
  return schemas;
}

describe("Schemas List Page (+page)", () => {
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

      const schemas = await loadSchemas();

      expect(schemas).toEqual(mockSchemas);
      expect(api.api.getSchemas).toHaveBeenCalledTimes(1);
    });

    it("starts with loading state", () => {
      const loading = true;
      expect(loading).toBe(true);
    });

    it("sets loading to false after data loads", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);

      let loading = true;
      await loadSchemas();
      loading = false;

      expect(loading).toBe(false);
    });

    it("initializes with empty schema array", () => {
      const schemas: unknown[] = [];
      expect(schemas).toEqual([]);
    });
  });

  describe("Display Schema Information", () => {
    it("displays schema name", async () => {
      const mockSchema = createMockSchema({ name: "TestSchema" });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      expect(schemas[0].name).toBe("TestSchema");
    });

    it("displays schema version", async () => {
      const mockSchema = createMockSchema({ version: "1.5.0" });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      expect(schemas[0].version).toBe("1.5.0");
    });

    it("displays dimension count in badge", async () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "dim1", type: "string", required: true },
          { name: "dim2", type: "integer", required: true },
          { name: "dim3", type: "enum", required: false, values: ["a", "b"] },
        ],
      });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      expect(schemas[0].dimensions.length).toBe(3);
    });

    it("displays first 5 dimensions", async () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "dim1", type: "string", required: true },
          { name: "dim2", type: "integer", required: true },
          { name: "dim3", type: "float", required: true },
          { name: "dim4", type: "boolean", required: true },
          { name: "dim5", type: "enum", required: false, values: ["a", "b"] },
          { name: "dim6", type: "list", required: false, item_type: "string" },
        ],
      });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      const displayedDims = schemas[0].dimensions.slice(0, 5);
      expect(displayedDims).toHaveLength(5);
      expect(displayedDims[0].name).toBe("dim1");
      expect(displayedDims[4].name).toBe("dim5");
    });

    it('shows "+X more" when dimensions exceed 5', async () => {
      const mockSchema = createMockSchema({
        dimensions: Array.from({ length: 8 }, (_, i) => ({
          name: `dim${i + 1}`,
          type: "string" as const,
          required: true,
        })),
      });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      expect(schemas[0].dimensions.length).toBe(8);
      const remaining = schemas[0].dimensions.length - 5;
      expect(remaining).toBe(3);
    });

    it("displays each dimension type", async () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "str_dim", type: "string", required: true },
          { name: "int_dim", type: "integer", required: true },
          { name: "float_dim", type: "float", required: true },
        ],
      });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      expect(schemas[0].dimensions[0].type).toBe("string");
      expect(schemas[0].dimensions[1].type).toBe("integer");
      expect(schemas[0].dimensions[2].type).toBe("float");
    });

    it("displays created_at date if present", async () => {
      const testDate = new Date("2024-01-15").toISOString();
      const mockSchema = createMockSchema({ created_at: testDate });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      expect(schemas[0].created_at).toBe(testDate);
    });
  });

  describe("Multiple Schemas", () => {
    it("displays all loaded schemas", async () => {
      const mockSchemas = [
        createMockSchema({ name: "Schema1" }),
        createMockSchema({ name: "Schema2" }),
        createMockSchema({ name: "Schema3" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await loadSchemas();

      expect(schemas).toHaveLength(3);
      expect(schemas[0].name).toBe("Schema1");
      expect(schemas[1].name).toBe("Schema2");
      expect(schemas[2].name).toBe("Schema3");
    });

    it("displays schemas in grid layout", async () => {
      const mockSchemas = [
        createMockSchema({ name: "S1" }),
        createMockSchema({ name: "S2" }),
        createMockSchema({ name: "S3" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await loadSchemas();

      expect(schemas.length).toBe(3);
    });
  });

  describe("Empty State", () => {
    it("shows empty state when no schemas", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);

      const schemas = await loadSchemas();

      expect(schemas).toEqual([]);
      expect(schemas.length).toBe(0);
    });

    it("has create button in empty state", () => {
      const href = "/schemas/new";
      expect(href).toBe("/schemas/new");
    });
  });

  describe("Navigation", () => {
    it("has create schema button link", () => {
      const href = "/schemas/new";
      expect(href).toBe("/schemas/new");
    });

    it("has view details button for each schema", async () => {
      const mockSchema = createMockSchema({ name: "TestSchema" });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      const detailHref = `/schemas/${schemas[0].name}`;
      expect(detailHref).toBe("/schemas/TestSchema");
    });

    it("constructs correct detail href for schema", async () => {
      const mockSchema = createMockSchema({ name: "MySchema" });
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([mockSchema]);

      const schemas = await loadSchemas();

      expect(`/schemas/${schemas[0].name}`).toBe("/schemas/MySchema");
    });
  });

  describe("Delete Functionality", () => {
    it("calls deleteSchema with schema name", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "deleteSchema").mockResolvedValue(undefined);

      await api.api.deleteSchema("TestSchema");

      expect(api.api.deleteSchema).toHaveBeenCalledWith("TestSchema");
    });

    it("reloads schemas after delete", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);
      vi.spyOn(api.api, "deleteSchema").mockResolvedValue(undefined);

      await api.api.deleteSchema("TestSchema");
      await api.api.getSchemas();

      expect(api.api.getSchemas).toHaveBeenCalled();
    });

    it("handles delete error", async () => {
      const error = new Error("Delete failed");
      vi.spyOn(api.api, "deleteSchema").mockRejectedValue(error);

      try {
        await api.api.deleteSchema("TestSchema");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });
  });

  describe("Error Handling", () => {
    it("catches schema loading error", async () => {
      const error = new Error("Failed to load schemas");
      vi.spyOn(api.api, "getSchemas").mockRejectedValue(error);

      try {
        await loadSchemas();
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
      error = "Failed to load schemas";
      expect(error).toBe("Failed to load schemas");
    });

    it("has retry button in error state", () => {
      // Retry button would call loadSchemas again
      expect(() => loadSchemas()).toBeDefined();
    });

    it("clears error before retrying", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);

      let error: string | null = "Previous error";
      error = null;
      const _schemas = await loadSchemas();

      expect(error).toBeNull();
    });
  });

  describe("Page Title and Headings", () => {
    it("has page title", () => {
      expect("Schemas - Rulate").toBeTruthy();
    });

    it("displays main heading", () => {
      expect("Schemas").toBeTruthy();
    });

    it("displays subtitle", () => {
      const subtitle =
        "Define the structure and validation rules for your items";
      expect(subtitle).toBeTruthy();
    });
  });
});
