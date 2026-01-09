/**
 * Pre-defined rule templates for common patterns
 */

export interface RuleTemplate {
  name: string;
  description: string;
  category: "exclusion" | "requirement";
  condition: object;
}

export const RULE_TEMPLATES: RuleTemplate[] = [
  {
    name: "Same Value Required",
    description: "Items must have the same value for a field",
    category: "requirement",
    condition: {
      equals: {
        field: "field_name",
      },
    },
  },
  {
    name: "Different Values Required",
    description: "Items must have different values for a field",
    category: "requirement",
    condition: {
      has_different: {
        field: "field_name",
      },
    },
  },
  {
    name: "Exclude Same Value",
    description: "Items cannot have the same value for a field",
    category: "exclusion",
    condition: {
      equals: {
        field: "field_name",
      },
    },
  },
  {
    name: "Exclude Same Without Different",
    description:
      "Items with the same value in one field must differ in another",
    category: "exclusion",
    condition: {
      all: [
        {
          equals: {
            field: "field1",
          },
        },
        {
          not: {
            has_different: {
              field: "field2",
            },
          },
        },
      ],
    },
  },
  {
    name: "Multiple Conditions (AND)",
    description: "All conditions must be true",
    category: "requirement",
    condition: {
      all: [
        {
          equals: {
            field: "field1",
          },
        },
        {
          has_different: {
            field: "field2",
          },
        },
      ],
    },
  },
  {
    name: "Multiple Conditions (OR)",
    description: "At least one condition must be true",
    category: "requirement",
    condition: {
      any: [
        {
          equals: {
            field: "field1",
          },
        },
        {
          equals: {
            field: "field2",
          },
        },
      ],
    },
  },
  {
    name: "Numeric Range",
    description: "Numeric values must be within a range",
    category: "requirement",
    condition: {
      abs_diff: {
        field: "numeric_field",
        operator: "<=",
        value: 2,
      },
    },
  },
  {
    name: "At Least One Has Value",
    description: "At least one item must have a specific value",
    category: "requirement",
    condition: {
      has_value: {
        field: "field_name",
        value: "required_value",
      },
    },
  },
  {
    name: "Formality Compatible",
    description: "Items must have compatible formality levels",
    category: "requirement",
    condition: {
      formality_compatible: {
        field: "formality",
        threshold: 1,
      },
    },
  },
  {
    name: "Shared List Items",
    description: "Items must share at least one value in a list field",
    category: "requirement",
    condition: {
      same_list_item: {
        field: "list_field",
      },
    },
  },
];

// Wardrobe-specific templates using the wardrobe schema
export const WARDROBE_TEMPLATES: RuleTemplate[] = [
  {
    name: "Same Body Zone - Different Layer",
    description: "Items on the same body zone must have different layers",
    category: "exclusion",
    condition: {
      all: [
        {
          equals: {
            field: "body_zone",
          },
        },
        {
          not: {
            has_different: {
              field: "layer",
            },
          },
        },
      ],
    },
  },
  {
    name: "Matching Season",
    description: "Items must be appropriate for the same season",
    category: "requirement",
    condition: {
      equals: {
        field: "season",
      },
    },
  },
  {
    name: "Similar Formality",
    description: "Items must have formality within 1 level of each other",
    category: "requirement",
    condition: {
      formality_compatible: {
        field: "formality",
        threshold: 1,
      },
    },
  },
  {
    name: "Matching Style",
    description: "Items must have the same style (casual, business, etc.)",
    category: "requirement",
    condition: {
      equals: {
        field: "style",
      },
    },
  },
  {
    name: "Shared Color",
    description: "Items must share at least one color",
    category: "requirement",
    condition: {
      same_list_item: {
        field: "colors",
      },
    },
  },
  {
    name: "Complete Outfit (Cluster)",
    description:
      "Outfit must cover different body zones with consistent formality",
    category: "requirement",
    condition: {
      all: [
        {
          unique_values: {
            field: "body_zone",
          },
        },
        {
          formality_range: {
            field: "formality",
            max_range: 1,
          },
        },
      ],
    },
  },
  {
    name: "Business Outfit Required",
    description: "Outfit must include at least one business item",
    category: "requirement",
    condition: {
      has_item_with: {
        field: "style",
        value: "business",
      },
    },
  },
];

// NOTE: Size constraints (min/max cluster size) are no longer available as rules.
// They are configured as search parameters in the UI filter controls.
export const CLUSTER_TEMPLATES: RuleTemplate[] = [
  {
    name: "Unique Field Values",
    description: "All items must have unique values for a field",
    category: "requirement",
    condition: {
      unique_values: {
        field: "field_name",
      },
    },
  },
  {
    name: "Must Include Item",
    description: "Cluster must include at least one item with a specific value",
    category: "requirement",
    condition: {
      has_item_with: {
        field: "field_name",
        value: "required_value",
      },
    },
  },
  {
    name: "Diversity Requirement",
    description: "Must have at least N different values for a field",
    category: "requirement",
    condition: {
      count_by_field: {
        field: "field_name",
        operator: ">=",
        value: 3,
      },
    },
  },
  {
    name: "Formality Range",
    description: "Formality levels must be within a range",
    category: "requirement",
    condition: {
      formality_range: {
        field: "formality",
        max_range: 2,
      },
    },
  },
  {
    name: "Cluster Composition",
    description: "Cluster must meet multiple criteria",
    category: "requirement",
    condition: {
      all: [
        {
          unique_values: {
            field: "body_zone",
          },
        },
        {
          formality_range: {
            field: "formality",
            max_range: 1,
          },
        },
      ],
    },
  },
];

export function getTemplatesByType(
  type: "pairwise" | "cluster",
): RuleTemplate[] {
  return type === "pairwise" ? RULE_TEMPLATES : CLUSTER_TEMPLATES;
}

export function formatTemplate(template: RuleTemplate): string {
  return JSON.stringify(template.condition, null, 2);
}
