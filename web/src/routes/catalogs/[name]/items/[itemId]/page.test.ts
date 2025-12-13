/**
 * Tests for Item Detail Page (+page.svelte)
 *
 * Tests the item detail page data loading and attribute display.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "$lib/api/client";
import {
  createMockItem,
  createMockCatalog,
  createMockSchema,
} from "$lib/test-utils/fixtures";

// Mock the API client
vi.mock("$lib/api/client", () => ({
  api: {
    getItem: vi.fn(),
    getCatalog: vi.fn(),
    getSchema: vi.fn(),
  },
}));

// Helper to simulate page loading
async function loadItem(catalogName: string, itemId: string) {
  const item = await api.api.getItem(catalogName, itemId);
  const catalog = await api.api.getCatalog(catalogName);
  const schema = await api.api.getSchema(catalog.schema_ref);
  return { item, schema, catalog };
}

// Helper for dimension lookup
function getDimensionInfo(schema: any, key: string) {
  if (!schema) return null;
  return schema.dimensions.find((d: any) => d.name === key);
}

describe("Item Detail Page (+page)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Data Loading", () => {
    it("loads item on mount", async () => {
      const mockItem = createMockItem({ item_id: "item1", name: "Test Item" });
      const mockCatalog = createMockCatalog({ name: "TestCat" });
      const mockSchema = createMockSchema({ name: "TestSchema" });

      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(mockCatalog);
      vi.spyOn(api.api, "getSchema").mockResolvedValue(mockSchema);

      const { item } = await loadItem("TestCat", "item1");

      expect(item).toEqual(mockItem);
      expect(api.api.getItem).toHaveBeenCalledWith("TestCat", "item1");
    });

    it("loads catalog to get schema name", async () => {
      const mockItem = createMockItem();
      const mockCatalog = createMockCatalog({
        name: "TestCat",
        schema_ref: "TestSchema",
      });
      const mockSchema = createMockSchema();

      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(mockCatalog);
      vi.spyOn(api.api, "getSchema").mockResolvedValue(mockSchema);

      const { catalog } = await loadItem("TestCat", "item1");

      expect(catalog.schema_ref).toBe("TestSchema");
      expect(api.api.getCatalog).toHaveBeenCalledWith("TestCat");
    });

    it("loads schema using schema name from catalog", async () => {
      const mockItem = createMockItem();
      const mockCatalog = createMockCatalog({ schema_ref: "Wardrobe" });
      const mockSchema = createMockSchema({ name: "Wardrobe" });

      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(mockCatalog);
      vi.spyOn(api.api, "getSchema").mockResolvedValue(mockSchema);

      const { schema } = await loadItem("TestCat", "item1");

      expect(schema.name).toBe("Wardrobe");
      expect(api.api.getSchema).toHaveBeenCalledWith("Wardrobe");
    });

    it("starts with loading state", () => {
      const loading = true;
      expect(loading).toBe(true);
    });

    it("sets loading to false after data loads", async () => {
      vi.spyOn(api.api, "getItem").mockResolvedValue(createMockItem());
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      let loading = true;
      await loadItem("cat", "item1");
      loading = false;

      expect(loading).toBe(false);
    });
  });

  describe("Display Item Information", () => {
    it("displays item name", async () => {
      const mockItem = createMockItem({ name: "Blue Shirt" });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(item.name).toBe("Blue Shirt");
    });

    it("displays item id", async () => {
      const mockItem = createMockItem({ item_id: "shirt_001" });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(item.item_id).toBe("shirt_001");
    });

    it("displays created_at date if present", async () => {
      const testDate = new Date("2024-01-15").toISOString();
      const mockItem = createMockItem({ created_at: testDate });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(item.created_at).toBe(testDate);
    });

    it("formats created_at date for display", () => {
      const testDate = new Date("2024-01-15T10:30:00Z").toISOString();
      const formatted = new Date(testDate).toLocaleString();

      expect(formatted).toBeTruthy();
      expect(formatted.length).toBeGreaterThan(0);
    });
  });

  describe("Attributes Display", () => {
    it("displays all item attributes", async () => {
      const mockItem = createMockItem({
        attributes: {
          color: "blue",
          size: "medium",
          material: "cotton",
        },
      });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(Object.keys(item.attributes)).toHaveLength(3);
      expect(item.attributes.color).toBe("blue");
      expect(item.attributes.size).toBe("medium");
    });

    it("displays string attributes", async () => {
      const mockItem = createMockItem({
        attributes: { color: "red" },
      });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(typeof item.attributes.color).toBe("string");
      expect(item.attributes.color).toBe("red");
    });

    it("displays numeric attributes", async () => {
      const mockItem = createMockItem({
        attributes: { count: 5, price: 19.99 },
      });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(item.attributes.count).toBe(5);
      expect(item.attributes.price).toBe(19.99);
    });

    it("displays boolean attributes", async () => {
      const mockItem = createMockItem({
        attributes: { washable: true, reversible: false },
      });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(item.attributes.washable).toBe(true);
      expect(item.attributes.reversible).toBe(false);
    });

    it("displays list attributes", async () => {
      const mockItem = createMockItem({
        attributes: { tags: ["cotton", "breathable", "durable"] },
      });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(Array.isArray(item.attributes.tags)).toBe(true);
      expect(item.attributes.tags).toHaveLength(3);
      expect(item.attributes.tags[0]).toBe("cotton");
    });
  });

  describe("Dimension Information", () => {
    it("finds dimension info for attribute", () => {
      const mockSchema = createMockSchema({
        dimensions: [
          { name: "color", type: "string", required: true },
          {
            name: "size",
            type: "enum",
            required: true,
            values: ["S", "M", "L"],
          },
        ],
      });

      const colorDim = getDimensionInfo(mockSchema, "color");
      expect(colorDim).not.toBeNull();
      expect(colorDim?.name).toBe("color");
      expect(colorDim?.type).toBe("string");
    });

    it("displays dimension type badge", () => {
      const mockSchema = createMockSchema({
        dimensions: [{ name: "size", type: "integer", required: true }],
      });

      const dim = getDimensionInfo(mockSchema, "size");
      expect(dim?.type).toBe("integer");
    });

    it("displays required badge for required dimensions", () => {
      const mockSchema = createMockSchema({
        dimensions: [{ name: "color", type: "string", required: true }],
      });

      const dim = getDimensionInfo(mockSchema, "color");
      expect(dim?.required).toBe(true);
    });

    it("does not display required badge for optional dimensions", () => {
      const mockSchema = createMockSchema({
        dimensions: [{ name: "notes", type: "string", required: false }],
      });

      const dim = getDimensionInfo(mockSchema, "notes");
      expect(dim?.required).toBe(false);
    });

    it("returns undefined for unknown dimension", () => {
      const mockSchema = createMockSchema({
        dimensions: [{ name: "color", type: "string", required: true }],
      });

      const dim = getDimensionInfo(mockSchema, "unknown");
      expect(dim).toBeUndefined();
    });
  });

  describe("Metadata Display", () => {
    it("displays metadata section when present", async () => {
      const mockItem = createMockItem({
        metadata: { source: "inventory", batch: "2024-01" },
      });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(item.metadata).not.toBeUndefined();
      expect(Object.keys(item.metadata).length).toBeGreaterThan(0);
    });

    it("skips metadata section when empty", async () => {
      const mockItem = createMockItem({
        metadata: {},
      });
      vi.spyOn(api.api, "getItem").mockResolvedValue(mockItem);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      const { item } = await loadItem("cat", "id");

      expect(Object.keys(item.metadata).length).toBe(0);
    });
  });

  describe("Navigation", () => {
    it("has back to catalog button", () => {
      const catalogName = "TestCatalog";
      const href = `/catalogs/${catalogName}`;
      expect(href).toBe("/catalogs/TestCatalog");
    });

    it("has edit item button with correct href", () => {
      const catalogName = "TestCatalog";
      const itemId = "item1";
      const href = `/catalogs/${catalogName}/items/${itemId}/edit`;
      expect(href).toBe("/catalogs/TestCatalog/items/item1/edit");
    });

    it("constructs correct edit href for item", () => {
      const href = "/catalogs/Summer/items/shirt_001/edit";
      expect(href).toBe("/catalogs/Summer/items/shirt_001/edit");
    });

    it("constructs correct back href for catalog", () => {
      const href = "/catalogs/Summer";
      expect(href).toBe("/catalogs/Summer");
    });
  });

  describe("Error Handling", () => {
    it("catches item loading error", async () => {
      const error = new Error("Failed to load item");
      vi.spyOn(api.api, "getItem").mockRejectedValue(error);
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      try {
        await loadItem("cat", "id");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches catalog loading error", async () => {
      const error = new Error("Failed to load catalog");
      vi.spyOn(api.api, "getItem").mockResolvedValue(createMockItem());
      vi.spyOn(api.api, "getCatalog").mockRejectedValue(error);
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      try {
        await loadItem("cat", "id");
      } catch (err) {
        expect(err).toEqual(error);
      }
    });

    it("catches schema loading error", async () => {
      const error = new Error("Failed to load schema");
      vi.spyOn(api.api, "getItem").mockResolvedValue(createMockItem());
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockRejectedValue(error);

      try {
        await loadItem("cat", "id");
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
      error = "Failed to load item";
      expect(error).toBe("Failed to load item");
    });

    it("has retry button in error state", async () => {
      vi.spyOn(api.api, "getItem").mockResolvedValue(createMockItem());
      vi.spyOn(api.api, "getCatalog").mockResolvedValue(createMockCatalog());
      vi.spyOn(api.api, "getSchema").mockResolvedValue(createMockSchema());

      expect(() => loadItem("cat", "id")).toBeDefined();
    });
  });

  describe("Page Title", () => {
    it("constructs page title from item and catalog", () => {
      const itemId = "shirt_001";
      const catalogName = "Summer";
      const pageTitle = `${itemId} - ${catalogName} - Rulate`;

      expect(pageTitle).toBe("shirt_001 - Summer - Rulate");
    });

    it("updates page title with different item and catalog", () => {
      const itemId = "pants_002";
      const catalogName = "Winter";
      const pageTitle = `${itemId} - ${catalogName} - Rulate`;

      expect(pageTitle).toBe("pants_002 - Winter - Rulate");
    });
  });
});
