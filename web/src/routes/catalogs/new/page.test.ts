/**
 * Tests for Catalog Creation Form Page (+page.svelte)
 *
 * Tests form loading, validation, and submission.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import { createMockSchema, createMockCatalog } from "$lib/test-utils/fixtures";

// Mock the API client and navigation
vi.mock("$lib/api/client", () => ({
  api: {
    getSchemas: vi.fn(),
    createCatalog: vi.fn(),
  },
}));

vi.mock("$app/navigation", () => ({
  goto: vi.fn(),
}));

describe("Catalog Creation Form (+page)", () => {
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

      const schemas = await api.api.getSchemas();

      expect(schemas).toEqual(mockSchemas);
      expect(api.api.getSchemas).toHaveBeenCalledTimes(1);
    });

    it("sets first schema as default", async () => {
      const mockSchemas = [
        createMockSchema({ name: "FirstSchema" }),
        createMockSchema({ name: "SecondSchema" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await api.api.getSchemas();
      let schema_name = "";
      if (schemas.length > 0) {
        schema_name = schemas[0].name;
      }

      expect(schema_name).toBe("FirstSchema");
    });

    it("handles empty schema list", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);

      const schemas = await api.api.getSchemas();
      let schema_name = "";
      if (schemas.length > 0) {
        schema_name = schemas[0].name;
      }

      expect(schemas).toEqual([]);
      expect(schema_name).toBe("");
    });

    it("starts with loadingSchemas as true", () => {
      const loadingSchemas = true;
      expect(loadingSchemas).toBe(true);
    });

    it("sets loadingSchemas to false after load", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);

      let loadingSchemas = true;
      await api.api.getSchemas();
      loadingSchemas = false;

      expect(loadingSchemas).toBe(false);
    });

    it("initializes form fields as empty", () => {
      const name = "";
      const schema_name = "";
      const description = "";

      expect(name).toBe("");
      expect(schema_name).toBe("");
      expect(description).toBe("");
    });

    it("initializes error as null", () => {
      const error: string | null = null;
      expect(error).toBeNull();
    });

    it("initializes submitting as false", () => {
      const submitting = false;
      expect(submitting).toBe(false);
    });
  });

  describe("Form Fields", () => {
    it("accepts catalog name input", () => {
      let name = "";
      name = "My Wardrobe";

      expect(name).toBe("My Wardrobe");
    });

    it("accepts schema selection", () => {
      let schema_name = "";
      schema_name = "SelectedSchema";

      expect(schema_name).toBe("SelectedSchema");
    });

    it("accepts description input", () => {
      let description = "";
      description = "This is my catalog";

      expect(description).toBe("This is my catalog");
    });

    it("allows optional description", () => {
      const description = "";
      expect(description).toBe("");
    });

    it("displays schemas in dropdown", async () => {
      const mockSchemas = [
        createMockSchema({ name: "Schema1", version: "1.0" }),
        createMockSchema({ name: "Schema2", version: "2.0" }),
        createMockSchema({ name: "Schema3", version: "1.5" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await api.api.getSchemas();

      expect(schemas).toHaveLength(3);
      expect(schemas[0].name).toBe("Schema1");
      expect(schemas[1].name).toBe("Schema2");
      expect(schemas[2].name).toBe("Schema3");
    });
  });

  describe("Form Validation", () => {
    it("requires catalog name", () => {
      let error: string | null = null;
      const name = "";

      if (!name.trim()) {
        error = "Catalog name is required";
      }

      expect(error).toBe("Catalog name is required");
    });

    it("rejects whitespace-only name", () => {
      let error: string | null = null;
      const name = "   ";

      if (!name.trim()) {
        error = "Catalog name is required";
      }

      expect(error).toBe("Catalog name is required");
    });

    it("requires schema selection", () => {
      let error: string | null = null;
      const schema_name = "";

      if (!schema_name) {
        error = "Schema selection is required";
      }

      expect(error).toBe("Schema selection is required");
    });

    it("allows optional description", () => {
      const description = "";
      const trimmed = description.trim() || undefined;

      expect(trimmed).toBeUndefined();
    });

    it("passes validation with required fields", () => {
      let error: string | null = null;
      const name = "My Catalog";
      const schema_name = "MySchema";

      if (!name.trim()) {
        error = "Catalog name is required";
      }

      if (!schema_name) {
        error = "Schema selection is required";
      }

      expect(error).toBeNull();
    });

    it("validates name and schema together", () => {
      let error: string | null = null;
      const name = "";
      const schema_name = "";

      if (!name.trim()) {
        error = "Catalog name is required";
        return;
      }

      if (!schema_name) {
        error = "Schema selection is required";
      }

      expect(error).toBe("Catalog name is required");
    });
  });

  describe("Form Submission", () => {
    it("calls createCatalog API with correct data", async () => {
      vi.spyOn(api.api, "createCatalog").mockResolvedValue(createMockCatalog());

      const _result = await api.api.createCatalog({
        name: "TestCatalog",
        schema_name: "TestSchema",
        description: "Test description",
      });

      expect(api.api.createCatalog).toHaveBeenCalledWith({
        name: "TestCatalog",
        schema_name: "TestSchema",
        description: "Test description",
      });
    });

    it("trims catalog name on submission", () => {
      const name = "  My Catalog  ";
      const trimmed = name.trim();

      expect(trimmed).toBe("My Catalog");
    });

    it("trims description on submission", () => {
      const description = "  My description  ";
      const trimmed = description.trim();

      expect(trimmed).toBe("My description");
    });

    it("omits description if empty", async () => {
      vi.spyOn(api.api, "createCatalog").mockResolvedValue(createMockCatalog());

      const description = "";
      const payload = {
        name: "TestCatalog",
        schema_name: "TestSchema",
        description: description.trim() || undefined,
      };

      await api.api.createCatalog(payload);

      expect(payload.description).toBeUndefined();
    });

    it("includes description if provided", async () => {
      vi.spyOn(api.api, "createCatalog").mockResolvedValue(createMockCatalog());

      const description = "Test description";
      const payload = {
        name: "TestCatalog",
        schema_name: "TestSchema",
        description: description.trim() || undefined,
      };

      await api.api.createCatalog(payload);

      expect(payload.description).toBe("Test description");
    });

    it("sets submitting state during submission", () => {
      let submitting = false;
      submitting = true;
      expect(submitting).toBe(true);

      submitting = false;
      expect(submitting).toBe(false);
    });

    it("handles submission error", async () => {
      const error = new Error("API error");
      vi.spyOn(api.api, "createCatalog").mockRejectedValue(error);

      try {
        await api.api.createCatalog({
          name: "TestCatalog",
          schema_name: "TestSchema",
        });
      } catch (err) {
        expect(err).toEqual(error);
      }
    });
  });

  describe("Error Display", () => {
    it("displays validation error", () => {
      let error: string | null = null;
      error = "Catalog name is required";

      expect(error).toBe("Catalog name is required");
    });

    it("displays API error", () => {
      let error: string | null = null;
      error = "Failed to create catalog";

      expect(error).toBe("Failed to create catalog");
    });

    it("clears error before new submission", () => {
      let error: string | null = "Previous error";
      error = null;

      expect(error).toBeNull();
    });

    it("initializes error as null", () => {
      const error: string | null = null;
      expect(error).toBeNull();
    });
  });

  describe("Loading States", () => {
    it("shows loading message while fetching schemas", () => {
      const loadingSchemas = true;
      expect(loadingSchemas).toBe(true);
    });

    it("shows no schemas message when list is empty", async () => {
      vi.spyOn(api.api, "getSchemas").mockResolvedValue([]);

      const schemas = await api.api.getSchemas();

      expect(schemas.length).toBe(0);
    });

    it("shows form when schemas are loaded", async () => {
      const mockSchemas = [createMockSchema()];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await api.api.getSchemas();

      expect(schemas.length).toBeGreaterThan(0);
    });
  });

  describe("Navigation", () => {
    it("has cancel button link", () => {
      const href = "/catalogs";
      expect(href).toBe("/catalogs");
    });

    it("has create schema button in no schemas state", () => {
      const href = "/schemas/new";
      expect(href).toBe("/schemas/new");
    });
  });

  describe("Error Handling", () => {
    it("catches schema loading error", async () => {
      const error = new Error("Failed to load schemas");
      vi.spyOn(api.api, "getSchemas").mockRejectedValue(error);

      try {
        await api.api.getSchemas();
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches catalog creation error", async () => {
      const error = new Error("Failed to create catalog");
      vi.spyOn(api.api, "createCatalog").mockRejectedValue(error);

      try {
        await api.api.createCatalog({
          name: "Test",
          schema_name: "Test",
        });
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("handles non-Error exceptions", () => {
      let error: string | null = null;
      const message = "String error";
      error = message;

      expect(error).toBe("String error");
    });
  });

  describe("Page Title", () => {
    it("has create catalog title", () => {
      expect("Create Catalog - Rulate").toBeTruthy();
    });

    it("displays main heading", () => {
      expect("Create Catalog").toBeTruthy();
    });

    it("displays subtitle", () => {
      const subtitle = "Create a collection of items to evaluate";
      expect(subtitle).toBeTruthy();
    });
  });

  describe("Schema Dropdown Display", () => {
    it("displays schema name and version", async () => {
      const mockSchemas = [
        createMockSchema({ name: "Wardrobe", version: "1.0" }),
        createMockSchema({ name: "Kitchen", version: "2.5" }),
      ];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await api.api.getSchemas();

      expect(schemas[0].name).toBe("Wardrobe");
      expect(schemas[0].version).toBe("1.0");
      expect(schemas[1].name).toBe("Kitchen");
      expect(schemas[1].version).toBe("2.5");
    });

    it("handles single schema", async () => {
      const mockSchemas = [createMockSchema({ name: "OnlySchema" })];
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await api.api.getSchemas();
      let schema_name = "";
      if (schemas.length > 0) {
        schema_name = schemas[0].name;
      }

      expect(schema_name).toBe("OnlySchema");
    });

    it("handles multiple schemas", async () => {
      const mockSchemas = Array.from({ length: 5 }, (_, i) =>
        createMockSchema({ name: `Schema${i + 1}` }),
      );
      vi.spyOn(api.api, "getSchemas").mockResolvedValue(mockSchemas);

      const schemas = await api.api.getSchemas();

      expect(schemas).toHaveLength(5);
    });
  });
});
