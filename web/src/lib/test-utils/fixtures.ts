/**
 * Test fixtures and mock data builders
 * Provides reusable mock objects for schemas, catalogs, items, and rulesets
 */

import type {
  Schema,
  Catalog,
  Item,
  RuleSet,
  ClusterRuleSet,
  ComparisonResult,
} from "$lib/api/client";

/**
 * Base mock schema with common dimension types
 */
export const mockSchema: Schema = {
  id: 1,
  name: "test-schema",
  version: "1.0.0",
  dimensions: [
    {
      name: "color",
      type: "enum",
      required: true,
      values: ["red", "blue", "green"],
    },
    {
      name: "size",
      type: "integer",
      required: true,
      min: 1,
      max: 10,
    },
    {
      name: "weight",
      type: "float",
      required: false,
      min: 0.1,
      max: 100.0,
    },
    {
      name: "tags",
      type: "list",
      required: false,
      item_type: "string",
    },
    {
      name: "active",
      type: "boolean",
      required: false,
    },
  ],
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

/**
 * Base mock catalog
 */
export const mockCatalog: Catalog = {
  id: 1,
  name: "test-catalog",
  schema_name: "test-schema",
  description: "Test catalog for testing",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

/**
 * Base mock item
 */
export const mockItem: Item = {
  id: 1,
  item_id: "item-001",
  name: "Test Item",
  attributes: {
    color: "red",
    size: 5,
    weight: 10.5,
    tags: ["tag1", "tag2"],
    active: true,
  },
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

/**
 * Base mock ruleset
 */
export const mockRuleSet: RuleSet = {
  id: 1,
  name: "test-ruleset",
  version: "1.0.0",
  schema_name: "test-schema",
  rules: [
    {
      name: "color-exclusion",
      type: "exclusion",
      enabled: true,
      condition: {
        equals: {
          field: "color",
        },
      },
    },
  ],
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

/**
 * Base mock cluster ruleset
 */
export const mockClusterRuleSet: ClusterRuleSet = {
  id: 1,
  name: "test-cluster-ruleset",
  version: "1.0.0",
  schema_name: "test-schema",
  pairwise_ruleset_name: "test-ruleset",
  rules: [],
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

/**
 * Base mock comparison result for a compatible pair
 */
export const mockCompatibleResult: ComparisonResult = {
  item1_id: "item-001",
  item2_id: "item-002",
  compatible: true,
  rule_evaluations: [
    {
      rule_name: "color-exclusion",
      rule_type: "exclusion",
      passed: true,
    },
  ],
};

/**
 * Base mock comparison result for an incompatible pair
 */
export const mockIncompatibleResult: ComparisonResult = {
  item1_id: "item-001",
  item2_id: "item-003",
  compatible: false,
  rule_evaluations: [
    {
      rule_name: "color-exclusion",
      rule_type: "exclusion",
      passed: false,
    },
  ],
};

// ============= Builder Functions =============

/**
 * Create a mock schema with optional overrides
 * @param overrides Partial schema properties to override
 * @returns Complete mock schema
 */
export function createMockSchema(overrides?: Partial<Schema>): Schema {
  return { ...mockSchema, ...overrides };
}

/**
 * Create a mock catalog with optional overrides
 * @param overrides Partial catalog properties to override
 * @returns Complete mock catalog
 */
export function createMockCatalog(overrides?: Partial<Catalog>): Catalog {
  return { ...mockCatalog, ...overrides };
}

/**
 * Create a mock item with optional overrides
 * @param overrides Partial item properties to override
 * @returns Complete mock item
 */
export function createMockItem(overrides?: Partial<Item>): Item {
  return { ...mockItem, ...overrides };
}

/**
 * Create a mock ruleset with optional overrides
 * @param overrides Partial ruleset properties to override
 * @returns Complete mock ruleset
 */
export function createMockRuleSet(overrides?: Partial<RuleSet>): RuleSet {
  return { ...mockRuleSet, ...overrides };
}

/**
 * Create a mock cluster ruleset with optional overrides
 * @param overrides Partial cluster ruleset properties to override
 * @returns Complete mock cluster ruleset
 */
export function createMockClusterRuleSet(
  overrides?: Partial<ClusterRuleSet>,
): ClusterRuleSet {
  return { ...mockClusterRuleSet, ...overrides };
}

// ============= Collection Builders =============

/**
 * Create an array of mock schemas
 * @param count Number of schemas to generate
 * @param baseOverrides Base overrides applied to each schema
 * @returns Array of mock schemas
 */
export function createMockSchemas(
  count: number,
  baseOverrides?: Partial<Schema>,
): Schema[] {
  return Array.from({ length: count }, (_, i) =>
    createMockSchema({
      id: i + 1,
      name: `schema-${String(i + 1).padStart(3, "0")}`,
      ...baseOverrides,
    }),
  );
}

/**
 * Create an array of mock items
 * @param count Number of items to generate
 * @param baseOverrides Base overrides applied to each item
 * @returns Array of mock items
 */
export function createMockItems(
  count: number,
  baseOverrides?: Partial<Item>,
): Item[] {
  return Array.from({ length: count }, (_, i) =>
    createMockItem({
      id: i + 1,
      item_id: `item-${String(i + 1).padStart(3, "0")}`,
      name: `Item ${i + 1}`,
      ...baseOverrides,
    }),
  );
}

/**
 * Create an array of mock rulesets
 * @param count Number of rulesets to generate
 * @param baseOverrides Base overrides applied to each ruleset
 * @returns Array of mock rulesets
 */
export function createMockRuleSets(
  count: number,
  baseOverrides?: Partial<RuleSet>,
): RuleSet[] {
  return Array.from({ length: count }, (_, i) =>
    createMockRuleSet({
      id: i + 1,
      name: `ruleset-${String(i + 1).padStart(3, "0")}`,
      ...baseOverrides,
    }),
  );
}

/**
 * Create an array of mock catalogs
 * @param count Number of catalogs to generate
 * @param baseOverrides Base overrides applied to each catalog
 * @returns Array of mock catalogs
 */
export function createMockCatalogs(
  count: number,
  baseOverrides?: Partial<Catalog>,
): Catalog[] {
  return Array.from({ length: count }, (_, i) =>
    createMockCatalog({
      id: i + 1,
      name: `catalog-${String(i + 1).padStart(3, "0")}`,
      ...baseOverrides,
    }),
  );
}

/**
 * Create a mock compatibility matrix (array of ComparisonResults)
 * @param items Array of items to create matrix for
 * @returns Array of comparison results for all pairs
 */
export function createMockComparisonMatrix(items: Item[]): ComparisonResult[] {
  const results: ComparisonResult[] = [];

  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      const compatible = Math.random() > 0.5;
      results.push({
        item1_id: items[i].item_id,
        item2_id: items[j].item_id,
        compatible,
        rule_evaluations: [
          {
            rule_name: "test-rule",
            rule_type: "exclusion",
            passed: compatible,
          },
        ],
      });
    }
  }

  return results;
}

/**
 * Create a simple mock schema for string enum field
 * @returns Mock schema with single enum dimension
 */
export function createSimpleEnumSchema(): Schema {
  return createMockSchema({
    name: "simple-schema",
    dimensions: [
      {
        name: "color",
        type: "enum",
        required: true,
        values: ["red", "blue", "green"],
      },
    ],
  });
}

/**
 * Create a simple mock schema for testing all dimension types
 * @returns Mock schema with one dimension of each type
 */
export function createAllTypesSchema(): Schema {
  return createMockSchema({
    name: "all-types-schema",
    dimensions: [
      {
        name: "string_field",
        type: "string",
        required: true,
      },
      {
        name: "integer_field",
        type: "integer",
        required: true,
        min: 1,
        max: 100,
      },
      {
        name: "float_field",
        type: "float",
        required: false,
        min: 0.1,
        max: 10.0,
      },
      {
        name: "boolean_field",
        type: "boolean",
        required: false,
      },
      {
        name: "enum_field",
        type: "enum",
        required: true,
        values: ["option1", "option2", "option3"],
      },
      {
        name: "list_field",
        type: "list",
        required: false,
        item_type: "string",
      },
    ],
  });
}
