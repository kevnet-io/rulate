/**
 * Tests for form attribute utilities
 */

import { describe, it, expect } from "vitest";
import {
  updateAttribute,
  getListValueAsString,
  initializeAttributes,
} from "./attributes";
import type { Dimension } from "$lib/api/client";

describe("Form Attributes Utilities", () => {
  describe("updateAttribute", () => {
    describe("Integer type", () => {
      const intDimension: Dimension = { name: "age", type: "integer" };

      it("converts string to integer", () => {
        const attrs = { age: 0 };
        const result = updateAttribute(attrs, "age", "25", intDimension);
        expect(result.age).toBe(25);
        expect(typeof result.age).toBe("number");
      });

      it("converts empty string to 0", () => {
        const attrs = { age: 25 };
        const result = updateAttribute(attrs, "age", "", intDimension);
        expect(result.age).toBe(0);
      });

      it("handles negative integers", () => {
        const attrs = { age: 0 };
        const result = updateAttribute(attrs, "age", "-5", intDimension);
        expect(result.age).toBe(-5);
      });

      it("handles decimal strings (truncates to integer)", () => {
        const attrs = { age: 0 };
        const result = updateAttribute(attrs, "age", "25.9", intDimension);
        expect(result.age).toBe(25);
      });
    });

    describe("Float type", () => {
      const floatDimension: Dimension = { name: "price", type: "float" };

      it("converts string to float", () => {
        const attrs = { price: 0 };
        const result = updateAttribute(attrs, "price", "19.99", floatDimension);
        expect(result.price).toBe(19.99);
        expect(typeof result.price).toBe("number");
      });

      it("converts empty string to 0", () => {
        const attrs = { price: 19.99 };
        const result = updateAttribute(attrs, "price", "", floatDimension);
        expect(result.price).toBe(0);
      });

      it("handles negative floats", () => {
        const attrs = { price: 0 };
        const result = updateAttribute(attrs, "price", "-5.5", floatDimension);
        expect(result.price).toBe(-5.5);
      });
    });

    describe("Boolean type", () => {
      const boolDimension: Dimension = { name: "active", type: "boolean" };

      it("sets boolean value", () => {
        const attrs = { active: false };
        const result = updateAttribute(attrs, "active", true, boolDimension);
        expect(result.active).toBe(true);
      });

      it("handles false value", () => {
        const attrs = { active: true };
        const result = updateAttribute(attrs, "active", false, boolDimension);
        expect(result.active).toBe(false);
      });
    });

    describe("List type", () => {
      it("parses comma-separated strings", () => {
        const listDimension: Dimension = { name: "tags", type: "list" };
        const attrs = { tags: [] };
        const result = updateAttribute(
          attrs,
          "tags",
          "red, blue, green",
          listDimension,
        );
        expect(result.tags).toEqual(["red", "blue", "green"]);
      });

      it("trims whitespace from list items", () => {
        const listDimension: Dimension = { name: "tags", type: "list" };
        const attrs = { tags: [] };
        const result = updateAttribute(
          attrs,
          "tags",
          "  a  ,  b  ,  c  ",
          listDimension,
        );
        expect(result.tags).toEqual(["a", "b", "c"]);
      });

      it("filters empty strings", () => {
        const listDimension: Dimension = { name: "tags", type: "list" };
        const attrs = { tags: [] };
        const result = updateAttribute(
          attrs,
          "tags",
          "a, , b, , c",
          listDimension,
        );
        expect(result.tags).toEqual(["a", "b", "c"]);
      });

      describe("Integer list items", () => {
        const intListDimension: Dimension = {
          name: "numbers",
          type: "list",
          item_type: "integer",
        };

        it("converts list items to integers", () => {
          const attrs = { numbers: [] };
          const result = updateAttribute(
            attrs,
            "numbers",
            "1, 2, 3",
            intListDimension,
          );
          expect(result.numbers).toEqual([1, 2, 3]);
          expect(
            result.numbers.every((n: unknown) => typeof n === "number"),
          ).toBe(true);
        });

        it("handles negative integers in list", () => {
          const attrs = { numbers: [] };
          const result = updateAttribute(
            attrs,
            "numbers",
            "-1, -2, -3",
            intListDimension,
          );
          expect(result.numbers).toEqual([-1, -2, -3]);
        });
      });

      describe("Float list items", () => {
        const floatListDimension: Dimension = {
          name: "values",
          type: "list",
          item_type: "float",
        };

        it("converts list items to floats", () => {
          const attrs = { values: [] };
          const result = updateAttribute(
            attrs,
            "values",
            "1.5, 2.5, 3.5",
            floatListDimension,
          );
          expect(result.values).toEqual([1.5, 2.5, 3.5]);
        });
      });

      describe("Boolean list items", () => {
        const boolListDimension: Dimension = {
          name: "flags",
          type: "list",
          item_type: "boolean",
        };

        it("converts list items to booleans", () => {
          const attrs = { flags: [] };
          const result = updateAttribute(
            attrs,
            "flags",
            "true, false, true",
            boolListDimension,
          );
          expect(result.flags).toEqual([true, false, true]);
        });

        it("handles case-insensitive true/false", () => {
          const attrs = { flags: [] };
          const result = updateAttribute(
            attrs,
            "flags",
            "TRUE, False, TrUe",
            boolListDimension,
          );
          expect(result.flags).toEqual([true, false, true]);
        });

        it("treats non-true strings as false", () => {
          const attrs = { flags: [] };
          const result = updateAttribute(
            attrs,
            "flags",
            "yes, no, 1",
            boolListDimension,
          );
          expect(result.flags).toEqual([false, false, false]);
        });
      });

      it("handles empty input", () => {
        const listDimension: Dimension = { name: "tags", type: "list" };
        const attrs = { tags: ["old"] };
        const result = updateAttribute(attrs, "tags", "", listDimension);
        expect(result.tags).toEqual([]);
      });
    });

    describe("Enum type", () => {
      it("sets enum value directly", () => {
        const enumDimension: Dimension = {
          name: "status",
          type: "enum",
          values: ["active", "inactive"],
        };
        const attrs = { status: "" };
        const result = updateAttribute(
          attrs,
          "status",
          "active",
          enumDimension,
        );
        expect(result.status).toBe("active");
      });
    });

    describe("String type", () => {
      it("sets string value directly", () => {
        const stringDimension: Dimension = { name: "name", type: "string" };
        const attrs = { name: "" };
        const result = updateAttribute(
          attrs,
          "name",
          "John Doe",
          stringDimension,
        );
        expect(result.name).toBe("John Doe");
      });
    });

    it("does not mutate original attributes object", () => {
      const attrs = { age: 0 };
      const dimension: Dimension = { name: "age", type: "integer" };
      updateAttribute(attrs, "age", "25", dimension);
      expect(attrs.age).toBe(0);
    });
  });

  describe("getListValueAsString", () => {
    it("joins array with comma and space", () => {
      const attrs = { tags: ["red", "blue", "green"] };
      const result = getListValueAsString(attrs, "tags");
      expect(result).toBe("red, blue, green");
    });

    it("handles single item list", () => {
      const attrs = { tags: ["red"] };
      const result = getListValueAsString(attrs, "tags");
      expect(result).toBe("red");
    });

    it("handles empty list", () => {
      const attrs = { tags: [] };
      const result = getListValueAsString(attrs, "tags");
      expect(result).toBe("");
    });

    it("handles number arrays", () => {
      const attrs = { numbers: [1, 2, 3] };
      const result = getListValueAsString(attrs, "numbers");
      expect(result).toBe("1, 2, 3");
    });

    it("returns empty string for non-array values", () => {
      const attrs = { value: "not an array" };
      const result = getListValueAsString(attrs, "value");
      expect(result).toBe("");
    });

    it("returns empty string for missing keys", () => {
      const attrs = {};
      const result = getListValueAsString(attrs, "missing");
      expect(result).toBe("");
    });
  });

  describe("initializeAttributes", () => {
    it("initializes boolean attributes to false", () => {
      const dimensions: Dimension[] = [
        { name: "active", type: "boolean" },
        { name: "verified", type: "boolean" },
      ];
      const result = initializeAttributes(dimensions);
      expect(result.active).toBe(false);
      expect(result.verified).toBe(false);
    });

    it("initializes list attributes to empty array", () => {
      const dimensions: Dimension[] = [{ name: "tags", type: "list" }];
      const result = initializeAttributes(dimensions);
      expect(result.tags).toEqual([]);
    });

    it("initializes integer attributes to min or 0", () => {
      const dimensions: Dimension[] = [
        { name: "age", type: "integer", min: 0 },
        { name: "count", type: "integer", min: 5 },
        { name: "value", type: "integer" },
      ];
      const result = initializeAttributes(dimensions);
      expect(result.age).toBe(0);
      expect(result.count).toBe(5);
      expect(result.value).toBe(0);
    });

    it("initializes float attributes to min or 0", () => {
      const dimensions: Dimension[] = [
        { name: "price", type: "float", min: 0 },
        { name: "rating", type: "float", min: 1.0 },
        { name: "score", type: "float" },
      ];
      const result = initializeAttributes(dimensions);
      expect(result.price).toBe(0);
      expect(result.rating).toBe(1.0);
      expect(result.score).toBe(0);
    });

    it("initializes enum attributes to first value", () => {
      const dimensions: Dimension[] = [
        {
          name: "status",
          type: "enum",
          values: ["active", "inactive", "pending"],
        },
      ];
      const result = initializeAttributes(dimensions);
      expect(result.status).toBe("active");
    });

    it("initializes enum with no values to empty string", () => {
      const dimensions: Dimension[] = [
        { name: "status", type: "enum", values: [] },
      ];
      const result = initializeAttributes(dimensions);
      expect(result.status).toBe("");
    });

    it("initializes string attributes to empty string", () => {
      const dimensions: Dimension[] = [{ name: "name", type: "string" }];
      const result = initializeAttributes(dimensions);
      expect(result.name).toBe("");
    });

    it("initializes all dimensions in schema", () => {
      const dimensions: Dimension[] = [
        { name: "id", type: "string" },
        { name: "active", type: "boolean" },
        { name: "age", type: "integer" },
        { name: "price", type: "float" },
        { name: "tags", type: "list" },
        { name: "status", type: "enum", values: ["a", "b"] },
      ];
      const result = initializeAttributes(dimensions);
      expect(result).toHaveProperty("id", "");
      expect(result).toHaveProperty("active", false);
      expect(result).toHaveProperty("age", 0);
      expect(result).toHaveProperty("price", 0);
      expect(result).toHaveProperty("tags", []);
      expect(result).toHaveProperty("status", "a");
    });

    it("returns empty object for empty dimensions", () => {
      const result = initializeAttributes([]);
      expect(result).toEqual({});
    });
  });
});
