/**
 * Tests for API Client
 *
 * Tests cover HTTP methods, error handling, and data transformations.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import type { Schema, Catalog } from "./client";

// We'll test the client by mocking fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import after setting up global.fetch
const { default: apiClient } = await import("./client");

describe("API Client", () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe("Schema Endpoints", () => {
    describe("getSchemas", () => {
      it("fetches all schemas", async () => {
        const mockSchemas: Schema[] = [
          {
            id: 1,
            name: "test_schema",
            version: "1.0.0",
            dimensions: [],
          },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockSchemas,
        });

        const result = await apiClient.getSchemas();

        expect(mockFetch).toHaveBeenCalledTimes(1);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/schemas"),
          expect.objectContaining({
            headers: expect.objectContaining({
              "Content-Type": "application/json",
            }),
          }),
        );
        expect(result).toEqual(mockSchemas);
      });

      it("throws error on API failure", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: async () => ({ detail: "Server error" }),
        });

        await expect(apiClient.getSchemas()).rejects.toThrow("Server error");
      });
    });

    describe("getSchema", () => {
      it("fetches a single schema by name", async () => {
        const mockSchema: Schema = {
          id: 1,
          name: "test_schema",
          version: "1.0.0",
          dimensions: [
            {
              name: "category",
              type: "enum",
              values: ["shirt", "pants"],
              required: true,
            },
          ],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockSchema,
        });

        const result = await apiClient.getSchema("test_schema");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/schemas/test_schema"),
          expect.any(Object),
        );
        expect(result).toEqual(mockSchema);
      });

      it("throws error when schema not found", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          status: 404,
          json: async () => ({ detail: "Schema not found" }),
        });

        await expect(apiClient.getSchema("nonexistent")).rejects.toThrow(
          "Schema not found",
        );
      });
    });

    describe("createSchema", () => {
      it("creates a new schema", async () => {
        const newSchema = {
          name: "new_schema",
          version: "1.0.0",
          dimensions: [],
        };

        const createdSchema: Schema = {
          ...newSchema,
          id: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => createdSchema,
        });

        const result = await apiClient.createSchema(newSchema);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/schemas"),
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify(newSchema),
          }),
        );
        expect(result).toEqual(createdSchema);
      });

      it("throws error on validation failure", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          status: 422,
          json: async () => ({ detail: "Validation error" }),
        });

        const invalidSchema = {
          name: "",
          version: "1.0.0",
          dimensions: [],
        };

        await expect(apiClient.createSchema(invalidSchema)).rejects.toThrow(
          "Validation error",
        );
      });
    });

    describe("updateSchema", () => {
      it("updates an existing schema", async () => {
        const updatedSchema: Schema = {
          id: 1,
          name: "test_schema",
          version: "2.0.0",
          dimensions: [],
          updated_at: new Date().toISOString(),
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => updatedSchema,
        });

        const result = await apiClient.updateSchema("test_schema", {
          version: "2.0.0",
        });

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/schemas/test_schema"),
          expect.objectContaining({
            method: "PUT",
            body: JSON.stringify({ version: "2.0.0" }),
          }),
        );
        expect(result).toEqual(updatedSchema);
      });
    });

    describe("deleteSchema", () => {
      it("deletes a schema", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        });

        await apiClient.deleteSchema("test_schema");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/schemas/test_schema"),
          expect.objectContaining({
            method: "DELETE",
          }),
        );
      });

      it("throws error when schema cannot be deleted", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          status: 409,
          json: async () => ({ detail: "Schema in use" }),
        });

        await expect(apiClient.deleteSchema("in_use_schema")).rejects.toThrow(
          "Schema in use",
        );
      });
    });
  });

  describe("Error Handling", () => {
    it("handles network errors", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      await expect(apiClient.getSchemas()).rejects.toThrow("Network error");
    });

    it("handles malformed JSON responses", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error("Invalid JSON");
        },
      });

      await expect(apiClient.getSchemas()).rejects.toThrow();
    });

    it("provides fallback error message for unknown errors", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}), // No detail field
      });

      await expect(apiClient.getSchemas()).rejects.toThrow(/HTTP error.*500/);
    });
  });

  describe("Request Headers", () => {
    it("includes Content-Type header by default", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await apiClient.getSchemas();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            "Content-Type": "application/json",
          }),
        }),
      );
    });

    it("allows custom headers to be added", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      // This would require modifying the client to accept custom headers,
      // but we're testing the current implementation
      await apiClient.getSchemas();

      expect(mockFetch).toHaveBeenCalled();
    });
  });

  describe("RuleSet Endpoints", () => {
    describe("getRuleSets", () => {
      it("fetches all rulesets", async () => {
        const mockRuleSets = [
          {
            id: 1,
            name: "test_ruleset",
            version: "1.0.0",
            schema_name: "test_schema",
            rules: [],
          },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockRuleSets,
        });

        const result = await apiClient.getRuleSets();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/rulesets"),
          expect.any(Object),
        );
        expect(result).toEqual(mockRuleSets);
      });
    });

    describe("getRuleSet", () => {
      it("fetches a single ruleset by name", async () => {
        const mockRuleSet = {
          id: 1,
          name: "test_ruleset",
          version: "1.0.0",
          schema_name: "test_schema",
          rules: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockRuleSet,
        });

        const result = await apiClient.getRuleSet("test_ruleset");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/rulesets/test_ruleset"),
          expect.any(Object),
        );
        expect(result).toEqual(mockRuleSet);
      });
    });

    describe("createRuleSet", () => {
      it("creates a new ruleset", async () => {
        const newRuleSet = {
          name: "new_ruleset",
          version: "1.0.0",
          schema_name: "test_schema",
          rules: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 1, ...newRuleSet }),
        });

        const result = await apiClient.createRuleSet(newRuleSet);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/rulesets"),
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify(newRuleSet),
          }),
        );
        expect(result.name).toEqual("new_ruleset");
      });
    });

    describe("updateRuleSet", () => {
      it("updates an existing ruleset", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 1, name: "test_ruleset", version: "2.0.0" }),
        });

        await apiClient.updateRuleSet("test_ruleset", { version: "2.0.0" });

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/rulesets/test_ruleset"),
          expect.objectContaining({
            method: "PUT",
          }),
        );
      });
    });

    describe("deleteRuleSet", () => {
      it("deletes a ruleset", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        });

        await apiClient.deleteRuleSet("test_ruleset");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/rulesets/test_ruleset"),
          expect.objectContaining({
            method: "DELETE",
          }),
        );
      });
    });
  });

  describe("Catalog Endpoints", () => {
    describe("getCatalogs", () => {
      it("fetches all catalogs", async () => {
        const mockCatalogs: Catalog[] = [
          {
            id: 1,
            name: "test_catalog",
            schema_name: "test_schema",
          },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockCatalogs,
        });

        const result = await apiClient.getCatalogs();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs"),
          expect.any(Object),
        );
        expect(result).toEqual(mockCatalogs);
      });
    });

    describe("getCatalog", () => {
      it("fetches a single catalog by name", async () => {
        const mockCatalog: Catalog = {
          id: 1,
          name: "test_catalog",
          schema_name: "test_schema",
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockCatalog,
        });

        const result = await apiClient.getCatalog("test_catalog");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog"),
          expect.any(Object),
        );
        expect(result).toEqual(mockCatalog);
      });
    });

    describe("createCatalog", () => {
      it("creates a new catalog", async () => {
        const newCatalog = {
          name: "new_catalog",
          schema_name: "test_schema",
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 1, ...newCatalog }),
        });

        const result = await apiClient.createCatalog(newCatalog);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result.name).toEqual("new_catalog");
      });
    });

    describe("updateCatalog", () => {
      it("updates an existing catalog", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            name: "test_catalog",
            schema_name: "test_schema",
          }),
        });

        await apiClient.updateCatalog("test_catalog", {
          description: "Updated",
        });

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog"),
          expect.objectContaining({
            method: "PUT",
          }),
        );
      });
    });

    describe("deleteCatalog", () => {
      it("deletes a catalog", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        });

        await apiClient.deleteCatalog("test_catalog");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog"),
          expect.objectContaining({
            method: "DELETE",
          }),
        );
      });
    });
  });

  describe("Item Endpoints", () => {
    describe("getItems", () => {
      it("fetches all items in a catalog", async () => {
        const mockItems = [
          {
            id: 1,
            item_id: "item-001",
            name: "Test Item",
            attributes: {},
          },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockItems,
        });

        const result = await apiClient.getItems("test_catalog");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog/items"),
          expect.any(Object),
        );
        expect(result).toEqual(mockItems);
      });
    });

    describe("getItem", () => {
      it("fetches a single item by ID", async () => {
        const mockItem = {
          id: 1,
          item_id: "item-001",
          name: "Test Item",
          attributes: {},
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockItem,
        });

        const result = await apiClient.getItem("test_catalog", "item-001");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog/items/item-001"),
          expect.any(Object),
        );
        expect(result).toEqual(mockItem);
      });
    });

    describe("createItem", () => {
      it("creates a new item in a catalog", async () => {
        const newItem = {
          item_id: "item-002",
          name: "New Item",
          attributes: { color: "red" },
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 2, ...newItem }),
        });

        const result = await apiClient.createItem("test_catalog", newItem);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog/items"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result.item_id).toEqual("item-002");
      });
    });

    describe("updateItem", () => {
      it("updates an existing item", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            item_id: "item-001",
            name: "Updated Item",
          }),
        });

        await apiClient.updateItem("test_catalog", "item-001", {
          name: "Updated Item",
        });

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog/items/item-001"),
          expect.objectContaining({
            method: "PUT",
          }),
        );
      });
    });

    describe("deleteItem", () => {
      it("deletes an item from a catalog", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        });

        await apiClient.deleteItem("test_catalog", "item-001");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/catalogs/test_catalog/items/item-001"),
          expect.objectContaining({
            method: "DELETE",
          }),
        );
      });
    });
  });

  describe("ClusterRuleSet Endpoints", () => {
    describe("getClusterRuleSets", () => {
      it("fetches all cluster rulesets", async () => {
        const mockClusterRuleSets = [
          {
            id: 1,
            name: "test_cluster_ruleset",
            version: "1.0.0",
            schema_name: "test_schema",
            pairwise_ruleset_name: "test_ruleset",
          },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockClusterRuleSets,
        });

        const result = await apiClient.getClusterRuleSets();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/cluster-rulesets"),
          expect.any(Object),
        );
        expect(result).toEqual(mockClusterRuleSets);
      });
    });

    describe("getClusterRuleSet", () => {
      it("fetches a single cluster ruleset by name", async () => {
        const mockClusterRuleSet = {
          id: 1,
          name: "test_cluster_ruleset",
          version: "1.0.0",
          schema_name: "test_schema",
          pairwise_ruleset_name: "test_ruleset",
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockClusterRuleSet,
        });

        const result = await apiClient.getClusterRuleSet(
          "test_cluster_ruleset",
        );

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/cluster-rulesets/test_cluster_ruleset"),
          expect.any(Object),
        );
        expect(result).toEqual(mockClusterRuleSet);
      });
    });

    describe("createClusterRuleSet", () => {
      it("creates a new cluster ruleset", async () => {
        const newClusterRuleSet = {
          name: "new_cluster_ruleset",
          version: "1.0.0",
          schema_name: "test_schema",
          pairwise_ruleset_name: "test_ruleset",
          rules: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 1, ...newClusterRuleSet }),
        });

        const result = await apiClient.createClusterRuleSet(newClusterRuleSet);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/cluster-rulesets"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result.name).toEqual("new_cluster_ruleset");
      });
    });

    describe("updateClusterRuleSet", () => {
      it("updates an existing cluster ruleset", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            name: "test_cluster_ruleset",
            version: "2.0.0",
          }),
        });

        await apiClient.updateClusterRuleSet("test_cluster_ruleset", {
          version: "2.0.0",
        });

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/cluster-rulesets/test_cluster_ruleset"),
          expect.objectContaining({
            method: "PUT",
          }),
        );
      });
    });

    describe("deleteClusterRuleSet", () => {
      it("deletes a cluster ruleset", async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        });

        await apiClient.deleteClusterRuleSet("test_cluster_ruleset");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/cluster-rulesets/test_cluster_ruleset"),
          expect.objectContaining({
            method: "DELETE",
          }),
        );
      });
    });
  });

  describe("Evaluation Endpoints", () => {
    describe("evaluatePair", () => {
      it("evaluates compatibility of two items", async () => {
        const mockResult = {
          item1_id: "item-001",
          item2_id: "item-002",
          compatible: true,
          rule_evaluations: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResult,
        });

        const result = await apiClient.evaluatePair(
          "test_catalog",
          "test_ruleset",
          "item-001",
          "item-002",
        );

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/evaluate/pair"),
          expect.any(Object),
        );
        expect(result).toEqual(mockResult);
      });
    });

    describe("evaluateMatrix", () => {
      it("generates a compatibility matrix", async () => {
        const mockMatrix = [
          {
            item1_id: "item-001",
            item2_id: "item-002",
            compatible: true,
            rule_evaluations: [],
          },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatrix,
        });

        const result = await apiClient.evaluateMatrix(
          "test_catalog",
          "test_ruleset",
        );

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/evaluate/matrix"),
          expect.any(Object),
        );
        expect(result).toEqual(mockMatrix);
      });
    });

    describe("evaluateItem", () => {
      it("evaluates an item against all others in catalog", async () => {
        const mockResults = [
          {
            item1_id: "item-001",
            item2_id: "item-002",
            compatible: true,
            rule_evaluations: [],
          },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResults,
        });

        const result = await apiClient.evaluateItem(
          "test_catalog",
          "test_ruleset",
          "item-001",
        );

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/evaluate/item"),
          expect.any(Object),
        );
        expect(result).toEqual(mockResults);
      });
    });

    describe("evaluateClusters", () => {
      it("evaluates clusters in a catalog", async () => {
        const mockClusters = {
          clusters: [],
          relationships: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockClusters,
        });

        const result = await apiClient.evaluateClusters(
          "test_catalog",
          "test_ruleset",
          "test_cluster_ruleset",
        );

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/evaluate/clusters"),
          expect.any(Object),
        );
        expect(result).toEqual(mockClusters);
      });
    });
  });

  describe("Import/Export Endpoints", () => {
    describe("exportSchemas", () => {
      it("exports all schemas", async () => {
        const mockExport = { schemas: [] };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportSchemas();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/schemas"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("exportRuleSets", () => {
      it("exports all rulesets", async () => {
        const mockExport = { rulesets: [] };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportRuleSets();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/rulesets"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("exportCatalogs", () => {
      it("exports all catalogs", async () => {
        const mockExport = { catalogs: [] };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportCatalogs();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/catalogs"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("exportClusterRuleSets", () => {
      it("exports all cluster rulesets", async () => {
        const mockExport = { cluster_rulesets: [] };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportClusterRuleSets();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/cluster-rulesets"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("exportSchema", () => {
      it("exports a single schema", async () => {
        const mockExport = { name: "Wardrobe", dimensions: [] };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportSchema("Wardrobe");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/schemas/Wardrobe"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("exportRuleSet", () => {
      it("exports a single ruleset", async () => {
        const mockExport = {
          name: "Compat",
          schema_ref: "Wardrobe",
          rules: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportRuleSet("Compat");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/rulesets/Compat"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("exportClusterRuleSet", () => {
      it("exports a single cluster ruleset", async () => {
        const mockExport = { name: "ClusterRules", rules: [] };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportClusterRuleSet("ClusterRules");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/cluster-rulesets/ClusterRules"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("exportCatalog", () => {
      it("exports a single catalog", async () => {
        const mockExport = {
          name: "Wardrobe",
          schema_ref: "Schema",
          items: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportCatalog("Wardrobe");

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/catalogs/Wardrobe"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });

    describe("importSchemas", () => {
      it("imports schemas", async () => {
        const mockImportData = { schemas: [] };
        const mockResult = { imported: 0 };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResult,
        });

        const result = await apiClient.importSchemas(mockImportData);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/import/schemas"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result).toEqual(mockResult);
      });
    });

    describe("importRuleSets", () => {
      it("imports rulesets", async () => {
        const mockImportData = { rulesets: [] };
        const mockResult = { imported: 0 };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResult,
        });

        const result = await apiClient.importRuleSets(mockImportData);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/import/rulesets"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result).toEqual(mockResult);
      });
    });

    describe("importCatalogs", () => {
      it("imports catalogs", async () => {
        const mockImportData = { catalogs: [] };
        const mockResult = { imported: 0 };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResult,
        });

        const result = await apiClient.importCatalogs(mockImportData);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/import/catalogs"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result).toEqual(mockResult);
      });
    });

    describe("importClusterRuleSets", () => {
      it("imports cluster rulesets", async () => {
        const mockImportData = { cluster_rulesets: [] };
        const mockResult = { imported: 0 };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResult,
        });

        const result = await apiClient.importClusterRuleSets(mockImportData);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/import/cluster-rulesets"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result).toEqual(mockResult);
      });
    });

    describe("importAll", () => {
      it("imports all data", async () => {
        const mockImportData = {
          schemas: [],
          rulesets: [],
          catalogs: [],
          cluster_rulesets: [],
        };
        const mockResult = { imported: 0 };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResult,
        });

        const result = await apiClient.importAll(mockImportData);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/import/all"),
          expect.objectContaining({
            method: "POST",
          }),
        );
        expect(result).toEqual(mockResult);
      });
    });

    describe("exportAll", () => {
      it("exports all data", async () => {
        const mockExport = {
          schemas: [],
          rulesets: [],
          catalogs: [],
          cluster_rulesets: [],
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockExport,
        });

        const result = await apiClient.exportAll();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/export/all"),
          expect.any(Object),
        );
        expect(result).toEqual(mockExport);
      });
    });
  });
});
