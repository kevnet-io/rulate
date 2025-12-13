/**
 * Tests for RuleEditor component
 *
 * Tests the RuleEditor's operator filtering, template filtering, and insertion logic.
 */

import { describe, it, expect } from 'vitest';
import { ALL_OPERATORS, type OperatorMetadata } from '$lib/data/operators';
import {
	RULE_TEMPLATES,
	CLUSTER_TEMPLATES,
	WARDROBE_TEMPLATES,
	formatTemplate,
	type RuleTemplate
} from '$lib/data/rule-templates';

// Extracted logic from RuleEditor component

function filterOperators(
	operators: OperatorMetadata[],
	category: string,
	searchTerm: string
): OperatorMetadata[] {
	let filtered = operators;

	if (category !== 'all') {
		filtered = filtered.filter((op) => op.category === category);
	}

	if (searchTerm) {
		const term = searchTerm.toLowerCase();
		filtered = filtered.filter(
			(op) =>
				op.name.toLowerCase().includes(term) ||
				op.displayName.toLowerCase().includes(term) ||
				op.description.toLowerCase().includes(term)
		);
	}

	return filtered;
}

function getTemplatesByCategory(
	category: string,
	isWardrobeSchema: boolean
): RuleTemplate[] {
	if (category === 'pairwise') {
		return RULE_TEMPLATES;
	} else if (category === 'cluster') {
		return CLUSTER_TEMPLATES;
	} else if (category === 'wardrobe') {
		return WARDROBE_TEMPLATES;
	} else {
		// 'all' category
		let templates = [...RULE_TEMPLATES, ...CLUSTER_TEMPLATES];
		if (isWardrobeSchema) {
			templates = [...templates, ...WARDROBE_TEMPLATES];
		}
		return templates;
	}
}

function generateOperatorTemplate(operator: OperatorMetadata): string {
	if (operator.parameters.some((p) => p.type === 'conditions')) {
		// Logical operator
		return `{\n  "${operator.name}": [\n    \n  ]\n}`;
	} else if (operator.parameters.length === 1 && operator.parameters[0].type === 'field') {
		// Field-only operator
		return `{\n  "${operator.name}": {\n    "field": ""\n  }\n}`;
	} else {
		// Complex operator
		const params = operator.parameters.map((p) => `"${p.name}": ""`).join(',\n    ');
		return `{\n  "${operator.name}": {\n    ${params}\n  }\n}`;
	}
}

function insertText(currentValue: string, newText: string): string {
	return currentValue ? currentValue + ',\n' + newText : newText;
}

describe('RuleEditor Component', () => {
	const allOperators = Object.values(ALL_OPERATORS);

	describe('Operator Filtering', () => {
		it('returns all operators when category is "all" and no search', () => {
			const filtered = filterOperators(allOperators, 'all', '');
			expect(filtered.length).toBe(allOperators.length);
		});

		it('filters operators by comparison category', () => {
			const filtered = filterOperators(allOperators, 'comparison', '');
			filtered.forEach((op) => {
				expect(op.category).toBe('comparison');
			});
			expect(filtered.length).toBeGreaterThan(0);
		});

		it('filters operators by logical category', () => {
			const filtered = filterOperators(allOperators, 'logical', '');
			filtered.forEach((op) => {
				expect(op.category).toBe('logical');
			});
			expect(filtered.length).toBeGreaterThan(0);
		});

		it('filters operators by field category', () => {
			const filtered = filterOperators(allOperators, 'field', '');
			filtered.forEach((op) => {
				expect(op.category).toBe('field');
			});
		});

		it('filters operators by cluster category', () => {
			const filtered = filterOperators(allOperators, 'cluster', '');
			filtered.forEach((op) => {
				expect(op.category).toBe('cluster');
			});
			expect(filtered.length).toBeGreaterThan(0);
		});

		it('filters operators by name search', () => {
			const filtered = filterOperators(allOperators, 'all', 'equals');
			expect(filtered.length).toBeGreaterThan(0);
			filtered.forEach((op) => {
				expect(op.name.toLowerCase()).toContain('equals');
			});
		});

		it('filters operators by display name search', () => {
			const filtered = filterOperators(allOperators, 'all', 'Equals');
			expect(filtered.length).toBeGreaterThan(0);
		});

		it('filters operators by description search', () => {
			const filtered = filterOperators(allOperators, 'all', 'same value');
			expect(filtered.length).toBeGreaterThan(0);
		});

		it('search is case-insensitive', () => {
			const lower = filterOperators(allOperators, 'all', 'equals');
			const upper = filterOperators(allOperators, 'all', 'EQUALS');
			expect(lower.length).toBe(upper.length);
		});

		it('combines category and search filters', () => {
			const filtered = filterOperators(allOperators, 'comparison', 'different');
			filtered.forEach((op) => {
				expect(op.category).toBe('comparison');
			});
			expect(filtered.length).toBeGreaterThan(0);
		});

		it('returns empty array when no matches', () => {
			const filtered = filterOperators(allOperators, 'all', 'nonexistentoperator123');
			expect(filtered).toEqual([]);
		});
	});

	describe('Template Filtering', () => {
		it('returns pairwise templates for "pairwise" category', () => {
			const templates = getTemplatesByCategory('pairwise', false);
			expect(templates).toEqual(RULE_TEMPLATES);
		});

		it('returns cluster templates for "cluster" category', () => {
			const templates = getTemplatesByCategory('cluster', false);
			expect(templates).toEqual(CLUSTER_TEMPLATES);
		});

		it('returns wardrobe templates for "wardrobe" category', () => {
			const templates = getTemplatesByCategory('wardrobe', false);
			expect(templates).toEqual(WARDROBE_TEMPLATES);
		});

		it('returns all templates for "all" category when not wardrobe schema', () => {
			const templates = getTemplatesByCategory('all', false);
			expect(templates.length).toBe(RULE_TEMPLATES.length + CLUSTER_TEMPLATES.length);
		});

		it('includes wardrobe templates for "all" category when is wardrobe schema', () => {
			const templates = getTemplatesByCategory('all', true);
			expect(templates.length).toBe(
				RULE_TEMPLATES.length + CLUSTER_TEMPLATES.length + WARDROBE_TEMPLATES.length
			);
		});

		it('excludes wardrobe templates when not wardrobe schema', () => {
			const templates = getTemplatesByCategory('all', false);
			const hasWardrobeTemplate = templates.some((t) =>
				WARDROBE_TEMPLATES.some((w) => w.name === t.name)
			);
			expect(hasWardrobeTemplate).toBe(false);
		});
	});

	describe('Operator Template Generation', () => {
		it('generates template for logical operator (all)', () => {
			const operator = allOperators.find((op) => op.name === 'all');
			expect(operator).toBeDefined();
			if (operator) {
				const template = generateOperatorTemplate(operator);
				expect(template).toContain('"all"');
				expect(template).toContain('[');
				expect(template).toContain(']');
			}
		});

		it('generates template for logical operator (any)', () => {
			const operator = allOperators.find((op) => op.name === 'any');
			expect(operator).toBeDefined();
			if (operator) {
				const template = generateOperatorTemplate(operator);
				expect(template).toContain('"any"');
				expect(template).toContain('[');
			}
		});

		it('generates template for field-only operator (equals)', () => {
			const operator = allOperators.find((op) => op.name === 'equals');
			expect(operator).toBeDefined();
			if (operator) {
				const template = generateOperatorTemplate(operator);
				expect(template).toContain('"equals"');
				expect(template).toContain('"field"');
				expect(template).toContain('""');
			}
		});

		it('generates template for field-only operator (has_different)', () => {
			const operator = allOperators.find((op) => op.name === 'has_different');
			expect(operator).toBeDefined();
			if (operator) {
				const template = generateOperatorTemplate(operator);
				expect(template).toContain('"has_different"');
				expect(template).toContain('"field"');
			}
		});

		it('generates template for complex operator (abs_diff)', () => {
			const operator = allOperators.find((op) => op.name === 'abs_diff');
			expect(operator).toBeDefined();
			if (operator) {
				const template = generateOperatorTemplate(operator);
				expect(template).toContain('"abs_diff"');
				expect(template).toContain('"field"');
				expect(template).toContain('"operator"');
				expect(template).toContain('"value"');
			}
		});

		it('generates template for complex operator (has_value)', () => {
			const operator = allOperators.find((op) => op.name === 'has_value');
			expect(operator).toBeDefined();
			if (operator) {
				const template = generateOperatorTemplate(operator);
				expect(template).toContain('"has_value"');
				expect(template).toContain('"field"');
				expect(template).toContain('"value"');
			}
		});

		it('generates valid JSON structure', () => {
			const operator = allOperators.find((op) => op.name === 'equals');
			if (operator) {
				const template = generateOperatorTemplate(operator);
				// Should parse as valid JSON (with placeholders filled)
				const filled = template.replace(/""/g, '"test"');
				expect(() => JSON.parse(filled)).not.toThrow();
			}
		});

		it('includes all required parameters in complex operator template', () => {
			const operator = allOperators.find((op) => op.name === 'abs_diff');
			if (operator) {
				const template = generateOperatorTemplate(operator);
				operator.parameters.forEach((param) => {
					expect(template).toContain(`"${param.name}"`);
				});
			}
		});
	});

	describe('Text Insertion', () => {
		it('inserts text into empty value', () => {
			const result = insertText('', '{"equals": {"field": "color"}}');
			expect(result).toBe('{"equals": {"field": "color"}}');
		});

		it('appends text to existing value with comma and newline', () => {
			const result = insertText(
				'{"equals": {"field": "color"}}',
				'{"has_different": {"field": "size"}}'
			);
			expect(result).toContain('{"equals": {"field": "color"}}');
			expect(result).toContain(',\n');
			expect(result).toContain('{"has_different": {"field": "size"}}');
		});

		it('handles multiple insertions', () => {
			let value = '';
			value = insertText(value, 'first');
			value = insertText(value, 'second');
			value = insertText(value, 'third');

			expect(value).toContain('first');
			expect(value).toContain('second');
			expect(value).toContain('third');
			// Should have 2 commas for 3 items
			expect(value.split(',').length).toBe(3);
		});
	});

	describe('Text Insertion at Cursor Position', () => {
		function insertAtCursorPosition(
			currentValue: string,
			newText: string,
			cursorStart: number,
			cursorEnd: number
		): { value: string; newCursorPosition: number } {
			const prefix = currentValue.slice(0, cursorStart);
			const suffix = currentValue.slice(cursorEnd);

			const needsCommaPrefix = prefix && !prefix.trimEnd().endsWith('[') && !prefix.trimEnd().endsWith('{');
			const needsCommaSuffix = suffix && !suffix.trimStart().startsWith(']') && !suffix.trimStart().startsWith('}') && !suffix.trimStart().startsWith(',');

			const value = prefix + (needsCommaPrefix ? ',\n' : '') + newText + (needsCommaSuffix ? ',\n' : '') + suffix;
			const newCursorPosition = cursorStart + (needsCommaPrefix ? 2 : 0) + newText.length;

			return { value, newCursorPosition };
		}

		it('inserts text at cursor start position', () => {
			const currentValue = '{"equals": {"field": "color"}}';
			const cursorStart = 0;
			const newText = '{"all": []}';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorStart);
			expect(result.value).toContain(newText);
			expect(result.value).toContain('{"equals"');
			expect(result.value.indexOf(newText)).toBeLessThan(result.value.indexOf('{"equals'));
		});

		it('inserts text at cursor middle position', () => {
			const currentValue = '{"all": [\n  \n]}';
			const cursorStart = 11; // Inside the array
			const newText = '{"equals": {"field": "color"}}';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorStart);
			expect(result.value).toContain(newText);
			expect(result.value).toContain('{"all": [');
		});

		it('replaces selected text when range is selected', () => {
			const currentValue = '{"old": "value"}';
			const cursorStart = 1;
			const cursorEnd = 6;
			const newText = '{"new": "value"}';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorEnd);
			expect(result.value).not.toContain('"old"');
			expect(result.value).toContain('"new"');
		});

		it('adds comma separator when needed before insertion', () => {
			const currentValue = '{"equals": {"field": "color"}}';
			const cursorStart = currentValue.length;
			const newText = '{"has_different": {"field": "size"}}';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorStart);
			expect(result.value).toContain(',\n');
		});

		it('does not add comma separator after opening bracket', () => {
			const currentValue = '{"all": [';
			const cursorStart = currentValue.length;
			const newText = '{"equals": {"field": "color"}}';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorStart);
			expect(result.value).not.toContain('[ ,');
		});

		it('does not add comma separator before closing bracket', () => {
			const currentValue = '{"all": [\n  {"equals": {"field": "color"}}\n]}';
			const cursorStart = currentValue.length - 2; // Before the closing bracket
			const newText = '{"has_different": {"field": "size"}}';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorStart);
			expect(result.value).not.toContain('} \n]}'); // Should have comma, but not space-comma
		});

		it('updates cursor position after insertion', () => {
			const currentValue = 'prefix';
			const cursorStart = 0;
			const newText = 'inserted_text';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorStart);
			expect(result.newCursorPosition).toBe(newText.length);
		});

		it('updates cursor position accounting for comma separator', () => {
			const currentValue = '{"equals": {"field": "color"}}';
			const cursorStart = currentValue.length;
			const newText = '{"has_different": {"field": "size"}}';

			const result = insertAtCursorPosition(currentValue, newText, cursorStart, cursorStart);
			// Should be: original position + ',\n'.length + newText.length
			expect(result.newCursorPosition).toBe(cursorStart + 2 + newText.length);
		});
	});

	describe('Rule Template Formatting', () => {
		it('formatTemplate returns valid JSON string', () => {
			const template = RULE_TEMPLATES[0];
			const formatted = formatTemplate(template);

			expect(() => JSON.parse(formatted)).not.toThrow();
		});

		it('formatTemplate includes condition from template', () => {
			const template = RULE_TEMPLATES.find((t) => t.name.includes('Same Value'));
			if (template) {
				const formatted = formatTemplate(template);
				const parsed = JSON.parse(formatted);

				expect(parsed).toEqual(template.condition);
			}
		});

		it('formatTemplate works for all pairwise templates', () => {
			RULE_TEMPLATES.forEach((template) => {
				const formatted = formatTemplate(template);
				expect(() => JSON.parse(formatted)).not.toThrow();
			});
		});

		it('formatTemplate works for all cluster templates', () => {
			CLUSTER_TEMPLATES.forEach((template) => {
				const formatted = formatTemplate(template);
				expect(() => JSON.parse(formatted)).not.toThrow();
			});
		});

		it('formatTemplate works for all wardrobe templates', () => {
			WARDROBE_TEMPLATES.forEach((template) => {
				const formatted = formatTemplate(template);
				expect(() => JSON.parse(formatted)).not.toThrow();
			});
		});

		it('formatted template is pretty-printed (has newlines)', () => {
			const template = RULE_TEMPLATES[0];
			const formatted = formatTemplate(template);

			expect(formatted).toContain('\n');
		});

		it('formatted template has indentation', () => {
			const template = RULE_TEMPLATES[0];
			const formatted = formatTemplate(template);

			expect(formatted).toContain('  '); // Should have 2-space indentation
		});
	});

	describe('Schema Field Detection', () => {
		it('detects wardrobe schema by name containing "wardrobe"', () => {
			const schemaName = 'wardrobe_schema';
			const isWardrobe = schemaName.toLowerCase().includes('wardrobe');
			expect(isWardrobe).toBe(true);
		});

		it('detects wardrobe schema case-insensitively', () => {
			const names = ['Wardrobe', 'WARDROBE', 'WaRdRoBe', 'my_wardrobe_schema'];
			names.forEach((name) => {
				const isWardrobe = name.toLowerCase().includes('wardrobe');
				expect(isWardrobe).toBe(true);
			});
		});

		it('does not detect non-wardrobe schemas', () => {
			const names = ['product_schema', 'catalog_schema', 'test_schema'];
			names.forEach((name) => {
				const isWardrobe = name.toLowerCase().includes('wardrobe');
				expect(isWardrobe).toBe(false);
			});
		});
	});

	describe('Operator Registry Validation', () => {
		it('all operators have required properties', () => {
			allOperators.forEach((op) => {
				expect(op).toHaveProperty('name');
				expect(op).toHaveProperty('displayName');
				expect(op).toHaveProperty('category');
				expect(op).toHaveProperty('description');
				expect(op).toHaveProperty('parameters');
				expect(op).toHaveProperty('examples');
				expect(op).toHaveProperty('icon');
			});
		});

		it('all operator parameters have required properties', () => {
			allOperators.forEach((op) => {
				op.parameters.forEach((param) => {
					expect(param).toHaveProperty('name');
					expect(param).toHaveProperty('type');
					expect(param).toHaveProperty('required');
					expect(param).toHaveProperty('description');
				});
			});
		});

		it('all operators have at least one example', () => {
			allOperators.forEach((op) => {
				expect(op.examples.length).toBeGreaterThan(0);
			});
		});

		it('all operators have non-empty descriptions', () => {
			allOperators.forEach((op) => {
				expect(op.description.length).toBeGreaterThan(0);
			});
		});
	});

	describe('Template Registry Validation', () => {
		it('all templates have required properties', () => {
			const allTemplates = [...RULE_TEMPLATES, ...CLUSTER_TEMPLATES, ...WARDROBE_TEMPLATES];
			allTemplates.forEach((template) => {
				expect(template).toHaveProperty('name');
				expect(template).toHaveProperty('description');
				expect(template).toHaveProperty('category');
				expect(template).toHaveProperty('condition');
			});
		});

		it('all templates have non-empty names', () => {
			const allTemplates = [...RULE_TEMPLATES, ...CLUSTER_TEMPLATES, ...WARDROBE_TEMPLATES];
			allTemplates.forEach((template) => {
				expect(template.name.length).toBeGreaterThan(0);
			});
		});

		it('all templates have non-empty descriptions', () => {
			const allTemplates = [...RULE_TEMPLATES, ...CLUSTER_TEMPLATES, ...WARDROBE_TEMPLATES];
			allTemplates.forEach((template) => {
				expect(template.description.length).toBeGreaterThan(0);
			});
		});

		it('all templates have valid category', () => {
			const allTemplates = [...RULE_TEMPLATES, ...CLUSTER_TEMPLATES, ...WARDROBE_TEMPLATES];
			const validCategories = ['exclusion', 'requirement'];
			allTemplates.forEach((template) => {
				expect(validCategories).toContain(template.category);
			});
		});

		it('wardrobe templates exist', () => {
			expect(WARDROBE_TEMPLATES.length).toBeGreaterThan(0);
		});

		it('wardrobe templates have "wardrobe" or clothing-related content', () => {
			WARDROBE_TEMPLATES.forEach((template) => {
				const content = JSON.stringify(template).toLowerCase();
				const nameAndDesc = (template.name + template.description).toLowerCase();
				// Should reference clothing/wardrobe concepts in content, name, or description
				const hasWardrobeContent =
					content.includes('layer') ||
					content.includes('body') ||
					content.includes('zone') ||
					content.includes('formal') ||
					content.includes('weather') ||
					content.includes('occasion') ||
					content.includes('material') ||
					nameAndDesc.includes('season') ||
					nameAndDesc.includes('style') ||
					nameAndDesc.includes('outfit') ||
					nameAndDesc.includes('formality') ||
					nameAndDesc.includes('color');

				expect(hasWardrobeContent).toBe(true);
			});
		});
	});

	describe('Context Detection for Smart Insertion', () => {
		// Helper constants mirroring RuleEditor implementation
		const InsertionContext = {
			EMPTY: 'EMPTY',
			INSIDE_ARRAY: 'INSIDE_ARRAY',
			SIMPLE_CONDITION: 'SIMPLE_CONDITION',
			COMPLEX_STRUCTURE: 'COMPLEX_STRUCTURE',
			INVALID_JSON: 'INVALID_JSON'
		} as const;

		type InsertionContextType = typeof InsertionContext[keyof typeof InsertionContext];

		function detectInsertionContext(value: string, cursorPos: number): InsertionContextType {
			// 1. Check if empty/whitespace
			if (!value.trim()) return InsertionContext.EMPTY;

			// 2. Try to parse JSON
			let parsed;
			try {
				parsed = JSON.parse(value);
			} catch {
				return InsertionContext.INVALID_JSON;
			}

			// 3. Check if cursor is inside an array of a logical operator
			const beforeCursor = value.slice(0, cursorPos);
			const openBrackets = (beforeCursor.match(/\[/g) || []).length;
			const closeBrackets = (beforeCursor.match(/\]/g) || []).length;
			const isInsideArray = openBrackets > closeBrackets;

			if (isInsideArray) {
				const logicalOps = ['all', 'any', 'not'];
				const hasLogicalOp = logicalOps.some((op) => beforeCursor.includes(`"${op}"`));
				if (hasLogicalOp) return InsertionContext.INSIDE_ARRAY;
			}

			// 4. Check if simple condition (single operator at root)
			const keys = Object.keys(parsed);
			if (keys.length === 1 && typeof parsed[keys[0]] === 'object') {
				return InsertionContext.SIMPLE_CONDITION;
			}

			// 5. Complex structure
			return InsertionContext.COMPLEX_STRUCTURE;
		}

		it('detects empty context for empty string', () => {
			const context = detectInsertionContext('', 0);
			expect(context).toBe(InsertionContext.EMPTY);
		});

		it('detects empty context for whitespace only', () => {
			const context = detectInsertionContext('   \n\t  ', 0);
			expect(context).toBe(InsertionContext.EMPTY);
		});

		it('detects simple condition for single operator at root', () => {
			const json = '{"equals": {"field": "color"}}';
			const context = detectInsertionContext(json, 0);
			expect(context).toBe(InsertionContext.SIMPLE_CONDITION);
		});

		it('detects simple condition for has_different operator', () => {
			const json = '{"has_different": {"field": "size"}}';
			const context = detectInsertionContext(json, 0);
			expect(context).toBe(InsertionContext.SIMPLE_CONDITION);
		});

		it('detects inside array when cursor is inside "all" array', () => {
			const json = '{"all": []}';
			const cursorPos = 9; // Inside the array
			const context = detectInsertionContext(json, cursorPos);
			expect(context).toBe(InsertionContext.INSIDE_ARRAY);
		});

		it('detects inside array when cursor is after opening bracket', () => {
			const json = '{"all": [\n  \n]}';
			const cursorPos = 10; // After opening bracket and newline
			const context = detectInsertionContext(json, cursorPos);
			expect(context).toBe(InsertionContext.INSIDE_ARRAY);
		});

		it('detects inside array when cursor is between array items', () => {
			const json = '{"all": [{"equals": {"field": "color"}}\n]}';
			const cursorPos = 40; // Before closing bracket (inside array)
			const context = detectInsertionContext(json, cursorPos);
			expect(context).toBe(InsertionContext.INSIDE_ARRAY);
		});

		it('detects inside array for "any" logical operator', () => {
			const json = '{"any": []}';
			const cursorPos = 9;
			const context = detectInsertionContext(json, cursorPos);
			expect(context).toBe(InsertionContext.INSIDE_ARRAY);
		});

		it('detects inside array for "not" logical operator', () => {
			const json = '{"not": []}';
			const cursorPos = 9;
			const context = detectInsertionContext(json, cursorPos);
			expect(context).toBe(InsertionContext.INSIDE_ARRAY);
		});

		it('detects complex structure for multiple conditions at root', () => {
			const json = '{"equals": {"field": "color"}, "has_different": {"field": "size"}}';
			const context = detectInsertionContext(json, 0);
			expect(context).toBe(InsertionContext.COMPLEX_STRUCTURE);
		});

		it('detects simple condition for logical operator with multiple items in array', () => {
			// A single root "all" operator is still SIMPLE_CONDITION even with multiple items
			const json = '{"all": [{"equals": {"field": "color"}}, {"has_different": {"field": "size"}}]}';
			const cursorPos = 0;
			const context = detectInsertionContext(json, cursorPos);
			expect(context).toBe(InsertionContext.SIMPLE_CONDITION);
		});

		it('detects invalid JSON for malformed input', () => {
			const json = '{invalid json}';
			const context = detectInsertionContext(json, 0);
			expect(context).toBe(InsertionContext.INVALID_JSON);
		});

		it('detects invalid JSON for unclosed braces', () => {
			const json = '{"equals": {"field": "color"';
			const context = detectInsertionContext(json, 0);
			expect(context).toBe(InsertionContext.INVALID_JSON);
		});

		it('detects invalid JSON for extra commas', () => {
			const json = '{"equals": {"field": "color",}}';
			const context = detectInsertionContext(json, 0);
			expect(context).toBe(InsertionContext.INVALID_JSON);
		});

		it('cursor position at root level is not treated as inside array', () => {
			const json = '{"equals": {"field": "color"}}';
			const cursorPos = 0; // At beginning
			const context = detectInsertionContext(json, cursorPos);
			expect(context).not.toBe(InsertionContext.INSIDE_ARRAY);
		});

		it('cursor outside array with nested array should not be inside array', () => {
			const json = '{"all": [{"equals": {"field": "color"}}]}';
			const cursorPos = json.length; // After closing bracket
			const context = detectInsertionContext(json, cursorPos);
			expect(context).not.toBe(InsertionContext.INSIDE_ARRAY);
		});
	});

	describe('Smart Insertion Logic', () => {
		function wrapInLogicalOperator(
			existingCondition: string,
			newOperator: string,
			operatorType: 'all' | 'any' = 'all'
		): string {
			return `{
  "${operatorType}": [
    ${existingCondition},
    ${newOperator}
  ]
}`;
		}

		it('wraps simple condition in "all" operator', () => {
			const existing = '{"equals": {"field": "color"}}';
			const newOp = '{"has_different": {"field": "size"}}';
			const result = wrapInLogicalOperator(existing, newOp, 'all');

			expect(result).toContain('"all"');
			expect(result).toContain('[');
			expect(result).toContain(existing);
			expect(result).toContain(newOp);

			// Should be valid JSON after filling empty fields
			const filled = result.replace(/""/g, '"test"');
			expect(() => JSON.parse(filled)).not.toThrow();
		});

		it('wraps simple condition in "any" operator', () => {
			const existing = '{"equals": {"field": "color"}}';
			const newOp = '{"has_different": {"field": "size"}}';
			const result = wrapInLogicalOperator(existing, newOp, 'any');

			expect(result).toContain('"any"');
			expect(result).toContain('[');
			expect(result).toContain(existing);
			expect(result).toContain(newOp);
		});

		it('maintains proper formatting when wrapping', () => {
			const existing = '{"equals": {"field": "color"}}';
			const newOp = '{"has_different": {"field": "size"}}';
			const result = wrapInLogicalOperator(existing, newOp, 'all');

			expect(result).toContain('\n');
			expect(result).toContain('  '); // Indentation
		});

		it('preserves existing condition exactly when wrapping', () => {
			const existing = '{"abs_diff": {"field": "price", "operator": ">", "value": 10}}';
			const newOp = '{"equals": {"field": "color"}}';
			const result = wrapInLogicalOperator(existing, newOp, 'all');

			// Existing condition should appear exactly as provided
			expect(result).toContain(existing);
		});
	});

	describe('Insertion with Smart Comma Logic', () => {
		function insertIntoArray(
			currentValue: string,
			newText: string,
			cursorStart: number
		): { value: string; newCursorPosition: number } {
			const prefix = currentValue.slice(0, cursorStart);
			const suffix = currentValue.slice(cursorStart);

			// Smart comma logic for array insertion
			const needsCommaPrefix =
				prefix.trimEnd() !== '' &&
				!prefix.trimEnd().endsWith('[') &&
				!prefix.trimEnd().endsWith(',');
			const needsCommaSuffix =
				suffix.trimStart() !== '' &&
				!suffix.trimStart().startsWith(']') &&
				!suffix.trimStart().startsWith(',');

			const value =
				prefix +
				(needsCommaPrefix ? ',\n' : '') +
				newText +
				(needsCommaSuffix ? ',\n' : '') +
				suffix;

			const newCursorPosition =
				cursorStart + (needsCommaPrefix ? 2 : 0) + newText.length;

			return { value, newCursorPosition };
		}

		it('inserts into empty array without extra commas', () => {
			const current = '{"all": []}';
			const newText = '{"equals": {"field": "color"}}';
			const result = insertIntoArray(current, newText, 9); // Position inside array

			expect(result.value).toContain('{"all": [');
			expect(result.value).toContain(newText);
			expect(result.value).toContain(']}');
			expect(result.value).not.toContain('[,');
			expect(result.value).not.toContain(',]');
		});

		it('inserts into array with existing item, adding comma before', () => {
			const current = '{"all": [{"equals": {"field": "color"}}]}';
			const newText = '{"has_different": {"field": "size"}}';
			const result = insertIntoArray(current, newText, 41); // Before closing bracket

			expect(result.value).toContain(',\n');
			expect(result.value).toContain(newText);
			expect(result.value).toContain(']}');
		});

		it('does not add comma after opening bracket', () => {
			const current = '{"all": [';
			const newText = '{"equals": {"field": "color"}}';
			const result = insertIntoArray(current, newText, 9);

			expect(result.value).not.toContain('[ ,');
			expect(result.value).not.toContain('[\n,');
		});

		it('does not add comma before closing bracket', () => {
			const current = '{"all": [{"equals": {"field": "color"}}\n]}';
			const newText = '{"has_different": {"field": "size"}}';
			const cursorPos = current.indexOf('\n]');
			const result = insertIntoArray(current, newText, cursorPos);

			// Should have comma before new text but not after
			expect(result.value).toContain(',\n' + newText + '\n]');
		});
	});
});
