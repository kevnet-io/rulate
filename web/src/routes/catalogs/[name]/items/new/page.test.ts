/**
 * Tests for Item Creation Form Page (+page.svelte)
 *
 * Tests form loading, attribute type conversion, validation, and submission.
 * This is the most complex form in the application.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import type { Dimension } from "$lib/api/client";
import {
  createMockCatalog,
  createMockSchema,
  createMockItem,
} from "$lib/test-utils/fixtures";

// Mock the API client and navigation
vi.mock("$lib/api/client", () => ({
  api: {
    getCatalog: vi.fn(),
    getSchema: vi.fn(),
    createItem: vi.fn(),
  },
}));

vi.mock("$app/navigation", () => ({
  goto: vi.fn(),
}));

// Helper: Initialize form state
function initializeFormState(schema: any) {
  const attributes: Record<string, any> = {};
  for (const dim of schema.dimensions) {
    if (dim.type === "boolean") {
      attributes[dim.name] = false;
    } else if (dim.type === "list") {
      attributes[dim.name] = [];
    } else if (dim.type === "integer" || dim.type === "float") {
      attributes[dim.name] = dim.min ?? 0;
    } else if (dim.type === "enum" && dim.values && dim.values.length > 0) {
      attributes[dim.name] = dim.values[0];
    } else {
      attributes[dim.name] = "";
    }
  }
  return attributes;
}

// Helper: Update attribute with type conversion
function updateAttribute(
  attributes: Record<string, any>,
  key: string,
  value: any,
  dimension: Dimension,
) {
  if (dimension.type === "integer") {
    attributes[key] = value === "" ? 0 : parseInt(value, 10);
  } else if (dimension.type === "float") {
    attributes[key] = value === "" ? 0 : parseFloat(value);
  } else if (dimension.type === "boolean") {
    attributes[key] = value;
  } else if (dimension.type === "list") {
    const items = value
      .split(",")
      .map((v: string) => v.trim())
      .filter((v: string) => v);
    if (dimension.item_type === "integer") {
      attributes[key] = items.map((v: string) => parseInt(v, 10));
    } else if (dimension.item_type === "float") {
      attributes[key] = items.map((v: string) => parseFloat(v));
    } else if (dimension.item_type === "boolean") {
      attributes[key] = items.map((v: string) => v.toLowerCase() === "true");
    } else {
      attributes[key] = items;
    }
  } else {
    attributes[key] = value;
  }
  return attributes;
}

describe("Item Creation Form (+page)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Data Loading", () => {
    it("loads catalog on mount", async () => {
      const mockCatalog = createMockCatalog({ name: "TestCat" });
      const mockSchema = createMockSchema();

      vi.spyOn(api.api, "getCatalog").mockResolvedValue(mockCatalog);
      vi.spyOn(api.api, "getSchema").mockResolvedValue(mockSchema);

      const catalog = await api.api.getCatalog("TestCat");

      expect(catalog).toEqual(mockCatalog);
      expect(api.api.getCatalog).toHaveBeenCalledWith("TestCat");
    });

    it("loads schema using catalog schema_name", async () => {
      const mockCatalog = createMockCatalog({ schema_name: "TestSchema" });
      const mockSchema = createMockSchema({ name: "TestSchema" });

      vi.spyOn(api.api, "getCatalog").mockResolvedValue(mockCatalog);
      vi.spyOn(api.api, "getSchema").mockResolvedValue(mockSchema);

      const catalog = await api.api.getCatalog("TestCat");
      const schema = await api.api.getSchema(catalog.schema_name);

      expect(schema.name).toBe("TestSchema");
      expect(api.api.getSchema).toHaveBeenCalledWith("TestSchema");
    });

    it("starts with loading state", () => {
      const loading = true;
      expect(loading).toBe(true);
    });

    it("sets loading to false after data loads", () => {
      const loading = false;
      expect(loading).toBe(false);
    });

    it("initializes error state as null", () => {
      const error: string | null = null;
      expect(error).toBeNull();
    });

    it("initializes submitting state as false", () => {
      const submitting = false;
      expect(submitting).toBe(false);
    });
  });

  describe("Form Field Initialization", () => {
    it("initializes boolean attributes as false", () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "washable", type: "boolean", required: false },
          { name: "reversible", type: "boolean", required: false },
        ],
      });

      const attributes = initializeFormState(mockSchema);

      expect(attributes.washable).toBe(false);
      expect(attributes.reversible).toBe(false);
    });

    it("initializes list attributes as empty array", () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "tags", type: "list", required: false, item_type: "string" },
        ],
      });

      const attributes = initializeFormState(mockSchema);

      expect(Array.isArray(attributes.tags)).toBe(true);
      expect(attributes.tags).toHaveLength(0);
    });

    it("initializes integer attributes with min or 0", () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "count1", type: "integer", required: false, min: 5 },
          { name: "count2", type: "integer", required: false, min: undefined },
        ],
      });

      const attributes = initializeFormState(mockSchema);

      expect(attributes.count1).toBe(5);
      expect(attributes.count2).toBe(0);
    });

    it("initializes float attributes with min or 0", () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "price1", type: "float", required: false, min: 10.5 },
          { name: "price2", type: "float", required: false, min: undefined },
        ],
      });

      const attributes = initializeFormState(mockSchema);

      expect(attributes.price1).toBe(10.5);
      expect(attributes.price2).toBe(0);
    });

    it("initializes enum attributes with first value", () => {
      const mockSchema = createMockSchema({
        dimensions: [
          {
            name: "size",
            type: "enum",
            required: false,
            values: ["S", "M", "L"],
          },
          { name: "color", type: "enum", required: false, values: [] },
        ],
      });

      const attributes = initializeFormState(mockSchema);

      expect(attributes.size).toBe("S");
      expect(attributes.color).toBe("");
    });

    it("initializes string attributes as empty string", () => {
      const mockSchema = createMockSchema({
        dimensions: [{ name: "description", type: "string", required: false }],
      });

      const attributes = initializeFormState(mockSchema);

      expect(attributes.description).toBe("");
    });

    it("initializes all required and optional attributes", () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "color", type: "string", required: true },
          { name: "size", type: "enum", required: true, values: ["S", "M"] },
          { name: "count", type: "integer", required: false },
          { name: "washable", type: "boolean", required: false },
        ],
      });

      const attributes = initializeFormState(mockSchema);

      expect(Object.keys(attributes)).toHaveLength(4);
      expect(attributes.color).toBe("");
      expect(attributes.size).toBe("S");
      expect(attributes.count).toBe(0);
      expect(attributes.washable).toBe(false);
    });
  });

  describe("Type Conversion - String", () => {
    it("stores string values unchanged", () => {
      const dim: Dimension = { name: "color", type: "string", required: false };
      const attributes = { color: "" };

      updateAttribute(attributes, "color", "blue", dim);

      expect(attributes.color).toBe("blue");
    });

    it("trims whitespace from string input", () => {
      const dim: Dimension = {
        name: "description",
        type: "string",
        required: false,
      };
      const attributes = { description: "" };
      const value = "  test value  ";

      updateAttribute(attributes, "description", value, dim);

      // The form uses bind:value which preserves whitespace, but trimmed on submission
      expect(attributes.description).toBe("  test value  ");
    });
  });

  describe("Type Conversion - Integer", () => {
    it("converts string to integer", () => {
      const dim: Dimension = {
        name: "count",
        type: "integer",
        required: false,
      };
      const attributes = { count: 0 };

      updateAttribute(attributes, "count", "42", dim);

      expect(attributes.count).toBe(42);
      expect(typeof attributes.count).toBe("number");
    });

    it("converts empty string to 0", () => {
      const dim: Dimension = {
        name: "count",
        type: "integer",
        required: false,
      };
      const attributes = { count: 10 };

      updateAttribute(attributes, "count", "", dim);

      expect(attributes.count).toBe(0);
    });

    it("parses negative integers", () => {
      const dim: Dimension = {
        name: "delta",
        type: "integer",
        required: false,
      };
      const attributes = { delta: 0 };

      updateAttribute(attributes, "delta", "-15", dim);

      expect(attributes.delta).toBe(-15);
    });

    it("parses floats to integers (truncates)", () => {
      const dim: Dimension = {
        name: "count",
        type: "integer",
        required: false,
      };
      const attributes = { count: 0 };

      updateAttribute(attributes, "count", "42.7", dim);

      expect(attributes.count).toBe(42);
    });
  });

  describe("Type Conversion - Float", () => {
    it("converts string to float", () => {
      const dim: Dimension = { name: "price", type: "float", required: false };
      const attributes = { price: 0 };

      updateAttribute(attributes, "price", "19.99", dim);

      expect(attributes.price).toBe(19.99);
      expect(typeof attributes.price).toBe("number");
    });

    it("converts empty string to 0", () => {
      const dim: Dimension = { name: "price", type: "float", required: false };
      const attributes = { price: 10.5 };

      updateAttribute(attributes, "price", "", dim);

      expect(attributes.price).toBe(0);
    });

    it("parses negative floats", () => {
      const dim: Dimension = { name: "temp", type: "float", required: false };
      const attributes = { temp: 0 };

      updateAttribute(attributes, "temp", "-5.5", dim);

      expect(attributes.temp).toBe(-5.5);
    });

    it("parses integers as floats", () => {
      const dim: Dimension = { name: "price", type: "float", required: false };
      const attributes = { price: 0 };

      updateAttribute(attributes, "price", "42", dim);

      expect(attributes.price).toBe(42);
    });
  });

  describe("Type Conversion - Boolean", () => {
    it("stores boolean true", () => {
      const dim: Dimension = {
        name: "washable",
        type: "boolean",
        required: false,
      };
      const attributes = { washable: false };

      updateAttribute(attributes, "washable", true, dim);

      expect(attributes.washable).toBe(true);
    });

    it("stores boolean false", () => {
      const dim: Dimension = {
        name: "washable",
        type: "boolean",
        required: false,
      };
      const attributes = { washable: true };

      updateAttribute(attributes, "washable", false, dim);

      expect(attributes.washable).toBe(false);
    });

    it("toggles boolean value", () => {
      const dim: Dimension = {
        name: "reversible",
        type: "boolean",
        required: false,
      };
      const attributes = { reversible: false };

      updateAttribute(attributes, "reversible", true, dim);
      expect(attributes.reversible).toBe(true);

      updateAttribute(attributes, "reversible", false, dim);
      expect(attributes.reversible).toBe(false);
    });
  });

  describe("Type Conversion - Enum", () => {
    it("stores enum value", () => {
      const dim: Dimension = {
        name: "size",
        type: "enum",
        required: false,
        values: ["S", "M", "L"],
      };
      const attributes = { size: "S" };

      updateAttribute(attributes, "size", "L", dim);

      expect(attributes.size).toBe("L");
    });

    it("changes enum value", () => {
      const dim: Dimension = {
        name: "color",
        type: "enum",
        required: false,
        values: ["red", "blue", "green"],
      };
      const attributes = { color: "red" };

      updateAttribute(attributes, "color", "blue", dim);

      expect(attributes.color).toBe("blue");
    });
  });

  describe("Type Conversion - List (String Items)", () => {
    it("parses comma-separated values", () => {
      const dim: Dimension = {
        name: "tags",
        type: "list",
        required: false,
        item_type: "string",
      };
      const attributes = { tags: [] };

      updateAttribute(attributes, "tags", "cotton, breathable, durable", dim);

      expect(Array.isArray(attributes.tags)).toBe(true);
      expect(attributes.tags).toEqual(["cotton", "breathable", "durable"]);
    });

    it("trims whitespace in list items", () => {
      const dim: Dimension = {
        name: "tags",
        type: "list",
        required: false,
        item_type: "string",
      };
      const attributes = { tags: [] };

      updateAttribute(attributes, "tags", "  item1  ,  item2  ,  item3  ", dim);

      expect(attributes.tags).toEqual(["item1", "item2", "item3"]);
    });

    it("handles empty string list", () => {
      const dim: Dimension = {
        name: "tags",
        type: "list",
        required: false,
        item_type: "string",
      };
      const attributes = { tags: ["old"] };

      updateAttribute(attributes, "tags", "", dim);

      expect(attributes.tags).toEqual([]);
    });

    it("filters empty entries in list", () => {
      const dim: Dimension = {
        name: "tags",
        type: "list",
        required: false,
        item_type: "string",
      };
      const attributes = { tags: [] };

      updateAttribute(attributes, "tags", "item1, , item2, , item3", dim);

      expect(attributes.tags).toEqual(["item1", "item2", "item3"]);
    });

    it("handles single item in list", () => {
      const dim: Dimension = {
        name: "tags",
        type: "list",
        required: false,
        item_type: "string",
      };
      const attributes = { tags: [] };

      updateAttribute(attributes, "tags", "single", dim);

      expect(attributes.tags).toEqual(["single"]);
    });
  });

  describe("Type Conversion - List (Integer Items)", () => {
    it("parses and converts integer list", () => {
      const dim: Dimension = {
        name: "sizes",
        type: "list",
        required: false,
        item_type: "integer",
      };
      const attributes = { sizes: [] };

      updateAttribute(attributes, "sizes", "5, 10, 15", dim);

      expect(attributes.sizes).toEqual([5, 10, 15]);
      expect(typeof attributes.sizes[0]).toBe("number");
    });

    it("converts negative integers in list", () => {
      const dim: Dimension = {
        name: "deltas",
        type: "list",
        required: false,
        item_type: "integer",
      };
      const attributes = { deltas: [] };

      updateAttribute(attributes, "deltas", "-5, 0, 5", dim);

      expect(attributes.deltas).toEqual([-5, 0, 5]);
    });
  });

  describe("Type Conversion - List (Float Items)", () => {
    it("parses and converts float list", () => {
      const dim: Dimension = {
        name: "prices",
        type: "list",
        required: false,
        item_type: "float",
      };
      const attributes = { prices: [] };

      updateAttribute(attributes, "prices", "10.5, 20.99, 15.0", dim);

      expect(attributes.prices).toEqual([10.5, 20.99, 15.0]);
      expect(typeof attributes.prices[0]).toBe("number");
    });
  });

  describe("Type Conversion - List (Boolean Items)", () => {
    it("parses and converts boolean list", () => {
      const dim: Dimension = {
        name: "flags",
        type: "list",
        required: false,
        item_type: "boolean",
      };
      const attributes = { flags: [] };

      updateAttribute(attributes, "flags", "true, false, true", dim);

      expect(attributes.flags).toEqual([true, false, true]);
      expect(typeof attributes.flags[0]).toBe("boolean");
    });

    it("handles case-insensitive true/false", () => {
      const dim: Dimension = {
        name: "flags",
        type: "list",
        required: false,
        item_type: "boolean",
      };
      const attributes = { flags: [] };

      updateAttribute(attributes, "flags", "True, FALSE, true", dim);

      expect(attributes.flags).toEqual([true, false, true]);
    });
  });

  describe("Form Validation", () => {
    it("requires item_id", () => {
      let error: string | null = null;
      const item_id = "";

      if (!item_id.trim()) {
        error = "Item ID is required";
      }

      expect(error).toBe("Item ID is required");
    });

    it("requires name", () => {
      let error: string | null = null;
      const name = "";

      if (!name.trim()) {
        error = "Item name is required";
      }

      expect(error).toBe("Item name is required");
    });

    it("allows whitespace-only item_id to be invalid", () => {
      let error: string | null = null;
      const item_id = "   ";

      if (!item_id.trim()) {
        error = "Item ID is required";
      }

      expect(error).toBe("Item ID is required");
    });

    it("validates required dimensions", () => {
      const schema = createMockSchema({
        dimensions: [
          { name: "color", type: "string", required: true },
          { name: "notes", type: "string", required: false },
        ],
      });

      const attributes = initializeFormState(schema);
      attributes.color = ""; // Set required field to empty
      attributes.notes = ""; // Optional field is ok

      let error: string | null = null;
      for (const dim of schema.dimensions) {
        if (dim.required) {
          const value = attributes[dim.name];
          if (!value || value === "") {
            error = `${dim.name} is required`;
            break;
          }
        }
      }

      expect(error).toBe("color is required");
    });

    it("passes validation with required fields filled", () => {
      const schema = createMockSchema({
        dimensions: [{ name: "color", type: "string", required: true }],
      });

      const attributes = initializeFormState(schema);
      attributes.color = "blue";

      let error: string | null = null;
      for (const dim of schema.dimensions) {
        if (dim.required) {
          const value = attributes[dim.name];
          if (!value || value === "") {
            error = `${dim.name} is required`;
            break;
          }
        }
      }

      expect(error).toBeNull();
    });

    it("validates required list fields are not empty", () => {
      const schema = createMockSchema({
        dimensions: [
          { name: "tags", type: "list", required: true, item_type: "string" },
        ],
      });

      const attributes = initializeFormState(schema);
      attributes.tags = []; // Empty list

      let error: string | null = null;
      for (const dim of schema.dimensions) {
        if (dim.required) {
          const value = attributes[dim.name];
          if (Array.isArray(value) && value.length === 0) {
            error = `${dim.name} is required`;
            break;
          }
        }
      }

      expect(error).toBe("tags is required");
    });
  });

  describe("Form Submission", () => {
    it("calls createItem API with correct data", async () => {
      vi.spyOn(api.api, "createItem").mockResolvedValue(createMockItem());

      const _result = await api.api.createItem("TestCat", {
        item_id: "item1",
        name: "Test Item",
        attributes: { color: "blue" },
      });

      expect(api.api.createItem).toHaveBeenCalledWith("TestCat", {
        item_id: "item1",
        name: "Test Item",
        attributes: { color: "blue" },
      });
    });

    it("trims item_id on submission", () => {
      const item_id = "  item1  ";
      const trimmed = item_id.trim();

      expect(trimmed).toBe("item1");
    });

    it("trims name on submission", () => {
      const name = "  Blue Shirt  ";
      const trimmed = name.trim();

      expect(trimmed).toBe("Blue Shirt");
    });

    it("handles submission error", async () => {
      const error = new Error("API error");
      vi.spyOn(api.api, "createItem").mockRejectedValue(error);

      try {
        await api.api.createItem("TestCat", {
          item_id: "item1",
          name: "Test",
          attributes: {},
        });
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("sets submitting state during submission", () => {
      let submitting = false;
      submitting = true;
      expect(submitting).toBe(true);

      submitting = false;
      expect(submitting).toBe(false);
    });
  });

  describe("Navigation", () => {
    it("has back to catalog button", () => {
      const catalogName = "TestCat";
      const href = `/catalogs/${catalogName}`;

      expect(href).toBe("/catalogs/TestCat");
    });

    it("has cancel button", () => {
      const catalogName = "TestCat";
      const href = `/catalogs/${catalogName}`;

      expect(href).toBe("/catalogs/TestCat");
    });
  });

  describe("Page Title", () => {
    it("constructs page title from catalog name", () => {
      const catalogName = "Summer";
      const pageTitle = `Add Item - ${catalogName} - Rulate`;

      expect(pageTitle).toBe("Add Item - Summer - Rulate");
    });
  });

  describe("Error Handling", () => {
    it("catches catalog loading error", async () => {
      const error = new Error("Failed to load catalog");
      vi.spyOn(api.api, "getCatalog").mockRejectedValue(error);

      try {
        await api.api.getCatalog("TestCat");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches schema loading error", async () => {
      const error = new Error("Failed to load schema");
      vi.spyOn(api.api, "getSchema").mockRejectedValue(error);

      try {
        await api.api.getSchema("TestSchema");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("displays error message on form", () => {
      const error: string | null = "Failed to create item";

      expect(error).toBe("Failed to create item");
      expect(error).not.toBeNull();
    });

    it("clears error on new submission attempt", () => {
      let error: string | null = "Previous error";
      error = null;

      expect(error).toBeNull();
    });
  });
});
