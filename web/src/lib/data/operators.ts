/**
 * Operator registry with metadata for the visual rule builder
 */

export type OperatorCategory = 'comparison' | 'logical' | 'field' | 'cluster';

export type ParameterType = 'field' | 'value' | 'conditions';

export interface OperatorParameter {
	name: string;
	type: ParameterType;
	required: boolean;
	description: string;
}

export interface OperatorMetadata {
	name: string;
	displayName: string;
	category: OperatorCategory;
	description: string;
	parameters: OperatorParameter[];
	examples: string[];
	icon: string;
}

// Pairwise operators
export const PAIRWISE_OPERATORS: Record<string, OperatorMetadata> = {
	equals: {
		name: 'equals',
		displayName: 'Equals',
		category: 'comparison',
		description: 'Check if both items have the same value for a field',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The field name to compare'
			}
		],
		examples: ['Items must have the same color', 'Items must be from the same season'],
		icon: '='
	},

	has_different: {
		name: 'has_different',
		displayName: 'Has Different',
		category: 'comparison',
		description: 'Check if items have different values for a field',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The field name to compare'
			}
		],
		examples: ['Items must have different colors', 'Items must have different layers'],
		icon: '≠'
	},

	abs_diff: {
		name: 'abs_diff',
		displayName: 'Absolute Difference',
		category: 'comparison',
		description: 'Check if the absolute difference between numeric values meets a condition',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The numeric field name'
			},
			{
				name: 'operator',
				type: 'value',
				required: true,
				description: 'Comparison operator (>, <, >=, <=, ==)'
			},
			{
				name: 'value',
				type: 'value',
				required: true,
				description: 'The threshold value'
			}
		],
		examples: ['Formality levels differ by more than 2', 'Prices differ by less than 10'],
		icon: '|Δ|'
	},

	has_value: {
		name: 'has_value',
		displayName: 'Has Value',
		category: 'field',
		description: 'Check if at least one item has a specific value',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The field name'
			},
			{
				name: 'value',
				type: 'value',
				required: true,
				description: 'The value to check for'
			}
		],
		examples: ['At least one item is waterproof', 'At least one item is formal'],
		icon: '∃'
	},

	all: {
		name: 'all',
		displayName: 'All',
		category: 'logical',
		description: 'All nested conditions must be true',
		parameters: [
			{
				name: 'conditions',
				type: 'conditions',
				required: true,
				description: 'Array of conditions that all must be true'
			}
		],
		examples: ['Items must match color AND season AND style'],
		icon: '∧'
	},

	any: {
		name: 'any',
		displayName: 'Any',
		category: 'logical',
		description: 'At least one nested condition must be true',
		parameters: [
			{
				name: 'conditions',
				type: 'conditions',
				required: true,
				description: 'Array of conditions where at least one must be true'
			}
		],
		examples: ['Items match color OR season OR style'],
		icon: '∨'
	},

	not: {
		name: 'not',
		displayName: 'Not',
		category: 'logical',
		description: 'Negate a condition',
		parameters: [
			{
				name: 'condition',
				type: 'conditions',
				required: true,
				description: 'The condition to negate'
			}
		],
		examples: ['Items do NOT have the same color', 'NOT waterproof'],
		icon: '¬'
	},

	same_list_item: {
		name: 'same_list_item',
		displayName: 'Same List Item',
		category: 'comparison',
		description: 'Check if items share at least one value in a list field',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The list field name'
			}
		],
		examples: ['Items share at least one tag', 'Items have a common material'],
		icon: '∩'
	},

	formality_compatible: {
		name: 'formality_compatible',
		displayName: 'Formality Compatible',
		category: 'comparison',
		description: 'Check if formality levels are compatible (within threshold)',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The formality field name'
			},
			{
				name: 'threshold',
				type: 'value',
				required: false,
				description: 'Maximum allowed difference (default: 1)'
			}
		],
		examples: ['Formality levels are within 1 point', 'Similar formality'],
		icon: '⚖'
	}
};

// Cluster operators
export const CLUSTER_OPERATORS: Record<string, OperatorMetadata> = {
	min_cluster_size: {
		name: 'min_cluster_size',
		displayName: 'Min Cluster Size',
		category: 'cluster',
		description: 'Require a minimum number of items in the cluster',
		parameters: [
			{
				name: 'size',
				type: 'value',
				required: true,
				description: 'Minimum number of items'
			}
		],
		examples: ['At least 3 items required', 'Minimum outfit size of 4 pieces'],
		icon: '#≥'
	},

	max_cluster_size: {
		name: 'max_cluster_size',
		displayName: 'Max Cluster Size',
		category: 'cluster',
		description: 'Limit the maximum number of items in the cluster',
		parameters: [
			{
				name: 'size',
				type: 'value',
				required: true,
				description: 'Maximum number of items'
			}
		],
		examples: ['No more than 5 items', 'Maximum outfit size of 6 pieces'],
		icon: '#≤'
	},

	unique_values: {
		name: 'unique_values',
		displayName: 'Unique Values',
		category: 'cluster',
		description: 'Require all items to have unique values for a field',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The field that must have unique values'
			}
		],
		examples: ['All items must have different body zones', 'Each item unique category'],
		icon: '≠*'
	},

	has_item_with: {
		name: 'has_item_with',
		displayName: 'Has Item With',
		category: 'cluster',
		description: 'Require at least one item matching a condition',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The field to check'
			},
			{
				name: 'value',
				type: 'value',
				required: true,
				description: 'The required value'
			}
		],
		examples: ['Must include at least one jacket', 'Must have a formal item'],
		icon: '∃='
	},

	count_by_field: {
		name: 'count_by_field',
		displayName: 'Count By Field',
		category: 'cluster',
		description: 'Count distinct values and compare to a threshold',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The field to count distinct values'
			},
			{
				name: 'operator',
				type: 'value',
				required: true,
				description: 'Comparison operator (>, <, >=, <=, ==)'
			},
			{
				name: 'value',
				type: 'value',
				required: true,
				description: 'The count threshold'
			}
		],
		examples: ['At least 3 different colors', 'No more than 2 patterns'],
		icon: '#('
	},

	formality_range: {
		name: 'formality_range',
		displayName: 'Formality Range',
		category: 'cluster',
		description: 'Check if formality levels are within a range',
		parameters: [
			{
				name: 'field',
				type: 'field',
				required: true,
				description: 'The formality field name'
			},
			{
				name: 'max_range',
				type: 'value',
				required: true,
				description: 'Maximum allowed range'
			}
		],
		examples: ['Formality range no more than 2 levels', 'Consistent formality'],
		icon: '⚖*'
	},

	cluster_all: {
		name: 'all',
		displayName: 'All (Cluster)',
		category: 'logical',
		description: 'All nested cluster conditions must be true',
		parameters: [
			{
				name: 'conditions',
				type: 'conditions',
				required: true,
				description: 'Array of conditions that all must be true'
			}
		],
		examples: ['Size between 3-5 AND unique body zones'],
		icon: '∧'
	},

	cluster_any: {
		name: 'any',
		displayName: 'Any (Cluster)',
		category: 'logical',
		description: 'At least one nested cluster condition must be true',
		parameters: [
			{
				name: 'conditions',
				type: 'conditions',
				required: true,
				description: 'Array of conditions where at least one must be true'
			}
		],
		examples: ['Has formal item OR has business item'],
		icon: '∨'
	},

	cluster_not: {
		name: 'not',
		displayName: 'Not (Cluster)',
		category: 'logical',
		description: 'Negate a cluster condition',
		parameters: [
			{
				name: 'condition',
				type: 'conditions',
				required: true,
				description: 'The condition to negate'
			}
		],
		examples: ['NOT all same color', 'Does NOT have casual item'],
		icon: '¬'
	}
};

export const ALL_OPERATORS = { ...PAIRWISE_OPERATORS, ...CLUSTER_OPERATORS };

export function getOperatorsByCategory(category: OperatorCategory) {
	return Object.values(ALL_OPERATORS).filter((op) => op.category === category);
}

export function getOperator(name: string): OperatorMetadata | undefined {
	return ALL_OPERATORS[name];
}
