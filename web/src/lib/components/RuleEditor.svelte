<script lang="ts">
	import { ALL_OPERATORS, type OperatorMetadata, getOperatorsByCategory } from '$lib/data/operators';
	import {
		RULE_TEMPLATES,
		CLUSTER_TEMPLATES,
		WARDROBE_TEMPLATES,
		formatTemplate,
		type RuleTemplate
	} from '$lib/data/rule-templates';
	import { toastStore } from '$lib/stores/toast.svelte';
	import Badge from './ui/badge/badge.svelte';
	import Button from './ui/button/button.svelte';
	import Card from './ui/card/card.svelte';
	import CardHeader from './ui/card/card-header.svelte';
	import CardTitle from './ui/card/card-title.svelte';
	import CardContent from './ui/card/card-content.svelte';

	interface Props {
		value: string;
		onchange?: (value: string) => void;
		schemaFields?: string[];
		schemaName?: string;  // Used to detect if wardrobe schema
	}

	let { value = $bindable(''), onchange, schemaFields = [], schemaName }: Props = $props();

	let textareaEl: HTMLTextAreaElement;
	let showSidebar = $state(true);
	let sidebarTab = $state<'operators' | 'templates'>('operators');
	let selectedCategory = $state<string>('all');
	let searchTerm = $state('');
	let selectedTemplateCategory = $state<string>('all');

	// Detect if using wardrobe schema
	const isWardrobeSchema = $derived(schemaName?.toLowerCase().includes('wardrobe'));

	// Insertion context detection constants
	const InsertionContext = {
		EMPTY: 'EMPTY',
		INSIDE_ARRAY: 'INSIDE_ARRAY',
		SIMPLE_CONDITION: 'SIMPLE_CONDITION',
		COMPLEX_STRUCTURE: 'COMPLEX_STRUCTURE',
		INVALID_JSON: 'INVALID_JSON'
	} as const;

	type InsertionContextType = typeof InsertionContext[keyof typeof InsertionContext];

	function detectInsertionContext(textValue: string, cursorPos: number): InsertionContextType {
		// 1. Check if empty/whitespace
		if (!textValue.trim()) return InsertionContext.EMPTY;

		// 2. Try to parse JSON
		let parsed;
		try {
			parsed = JSON.parse(textValue);
		} catch {
			return InsertionContext.INVALID_JSON;
		}

		// 3. Check if cursor is inside an array of a logical operator
		const beforeCursor = textValue.slice(0, cursorPos);
		const afterCursor = textValue.slice(cursorPos);

		// Count brackets to determine if we're inside an array
		const openBrackets = (beforeCursor.match(/\[/g) || []).length;
		const closeBrackets = (beforeCursor.match(/\]/g) || []).length;
		const isInsideArray = openBrackets > closeBrackets;

		if (isInsideArray) {
			// Check if this array belongs to a logical operator
			const logicalOps = ['all', 'any', 'not'];
			const hasLogicalOp = logicalOps.some(op => beforeCursor.includes(`"${op}"`));
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

	function updateCursorPosition(position: number) {
		setTimeout(() => {
			if (textareaEl) {
				textareaEl.selectionStart = position;
				textareaEl.selectionEnd = position;
				textareaEl.focus();
			}
		}, 0);
	}

	const categories = [
		{ value: 'all', label: 'All Operators' },
		{ value: 'comparison', label: 'Comparison' },
		{ value: 'logical', label: 'Logical' },
		{ value: 'field', label: 'Field' },
		{ value: 'cluster', label: 'Cluster' }
	];

	const filteredOperators = $derived(() => {
		let operators = Object.values(ALL_OPERATORS);

		if (selectedCategory !== 'all') {
			operators = operators.filter((op) => op.category === selectedCategory);
		}

		if (searchTerm) {
			const term = searchTerm.toLowerCase();
			operators = operators.filter(
				(op) =>
					op.name.toLowerCase().includes(term) ||
					op.displayName.toLowerCase().includes(term) ||
					op.description.toLowerCase().includes(term)
			);
		}

		return operators;
	});

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

	function insertOperator(operator: OperatorMetadata, action: 'insert' | 'replace' = 'insert') {
		const template = generateOperatorTemplate(operator);

		if (!textareaEl) {
			// Fallback: just set the value
			value = template;
			if (onchange) onchange(value);
			return;
		}

		const start = textareaEl.selectionStart;
		const end = textareaEl.selectionEnd;
		const context = detectInsertionContext(value, start);

		if (action === 'replace') {
			// Replace entire content or selection
			if (start !== end) {
				// Replace selection
				value = value.slice(0, start) + template + value.slice(end);
				updateCursorPosition(start + template.length);
			} else {
				// Replace entire content
				value = template;
				updateCursorPosition(template.length);
			}
			if (onchange) onchange(value);
			return;
		}

		// Smart insertion based on context
		switch (context) {
			case InsertionContext.EMPTY:
				value = template;
				updateCursorPosition(template.length);
				break;

			case InsertionContext.INSIDE_ARRAY: {
				// Insert into the array at cursor position
				const prefix = value.slice(0, start);
				const suffix = value.slice(end);

				// Smart comma handling for arrays
				const needsCommaPrefix = prefix.trimEnd() !== '' &&
					!prefix.trimEnd().endsWith('[') &&
					!prefix.trimEnd().endsWith(',');
				const needsCommaSuffix = suffix.trimStart() !== '' &&
					!suffix.trimStart().startsWith(']') &&
					!suffix.trimStart().startsWith(',');

				value = prefix +
					(needsCommaPrefix ? ',\n' : '') +
					template +
					(needsCommaSuffix ? ',\n' : '') +
					suffix;

				updateCursorPosition(start + (needsCommaPrefix ? 2 : 0) + template.length);
				break;
			}

			case InsertionContext.SIMPLE_CONDITION: {
				// Wrap both in 'all'
				const existingCondition = value.trim();
				value = wrapInLogicalOperator(existingCondition, template, 'all');
				updateCursorPosition(value.length);
				break;
			}

			case InsertionContext.COMPLEX_STRUCTURE:
			case InsertionContext.INVALID_JSON:
			default: {
				// Insert at cursor with smart comma logic
				const prefix = value.slice(0, start);
				const suffix = value.slice(end);

				const needsComma = prefix.trimEnd() !== '' &&
					!prefix.trimEnd().endsWith('[') &&
					!prefix.trimEnd().endsWith('{');

				value = prefix +
					(needsComma ? ',\n' : '') +
					template +
					suffix;

				updateCursorPosition(start + (needsComma ? 2 : 0) + template.length);
				break;
			}
		}

		if (onchange) onchange(value);
	}

	const templateCategories = $derived([
		{ value: 'all', label: 'All Templates' },
		{ value: 'pairwise', label: 'Pairwise' },
		{ value: 'cluster', label: 'Cluster' },
		...(isWardrobeSchema ? [{ value: 'wardrobe', label: 'Wardrobe Examples' }] : [])
	]);

	const filteredTemplates = $derived(() => {
		let templates: RuleTemplate[] = [];

		if (selectedTemplateCategory === 'pairwise') {
			templates = RULE_TEMPLATES;
		} else if (selectedTemplateCategory === 'cluster') {
			templates = CLUSTER_TEMPLATES;
		} else if (selectedTemplateCategory === 'wardrobe') {
			templates = WARDROBE_TEMPLATES;
		} else {
			templates = [...RULE_TEMPLATES, ...CLUSTER_TEMPLATES];
			if (isWardrobeSchema) {
				templates = [...templates, ...WARDROBE_TEMPLATES];
			}
		}

		return templates;
	});

	function insertTemplate(template: RuleTemplate, action: 'insert' | 'replace' = 'insert') {
		const templateJson = formatTemplate(template);

		if (!textareaEl) {
			// Fallback: just set the value
			value = templateJson;
			if (onchange) onchange(value);
			return;
		}

		const start = textareaEl.selectionStart;
		const end = textareaEl.selectionEnd;
		const context = detectInsertionContext(value, start);

		if (action === 'replace') {
			// Replace entire content or selection
			if (start !== end) {
				// Replace selection
				value = value.slice(0, start) + templateJson + value.slice(end);
				updateCursorPosition(start + templateJson.length);
			} else {
				// Replace entire content
				value = templateJson;
				updateCursorPosition(templateJson.length);
			}
			if (onchange) onchange(value);
			return;
		}

		// Smart insertion based on context
		switch (context) {
			case InsertionContext.EMPTY:
				value = templateJson;
				updateCursorPosition(templateJson.length);
				break;

			case InsertionContext.INSIDE_ARRAY: {
				// Insert into the array at cursor position
				const prefix = value.slice(0, start);
				const suffix = value.slice(end);

				// Smart comma handling for arrays
				const needsCommaPrefix = prefix.trimEnd() !== '' &&
					!prefix.trimEnd().endsWith('[') &&
					!prefix.trimEnd().endsWith(',');
				const needsCommaSuffix = suffix.trimStart() !== '' &&
					!suffix.trimStart().startsWith(']') &&
					!suffix.trimStart().startsWith(',');

				value = prefix +
					(needsCommaPrefix ? ',\n' : '') +
					templateJson +
					(needsCommaSuffix ? ',\n' : '') +
					suffix;

				updateCursorPosition(start + (needsCommaPrefix ? 2 : 0) + templateJson.length);
				break;
			}

			case InsertionContext.SIMPLE_CONDITION: {
				// Wrap both in 'all'
				const existingCondition = value.trim();
				value = wrapInLogicalOperator(existingCondition, templateJson, 'all');
				updateCursorPosition(value.length);
				break;
			}

			case InsertionContext.COMPLEX_STRUCTURE:
			case InsertionContext.INVALID_JSON:
			default: {
				// Insert at cursor with smart comma logic
				const prefix = value.slice(0, start);
				const suffix = value.slice(end);

				const needsComma = prefix.trimEnd() !== '' &&
					!prefix.trimEnd().endsWith('[') &&
					!prefix.trimEnd().endsWith('{');

				value = prefix +
					(needsComma ? ',\n' : '') +
					templateJson +
					suffix;

				updateCursorPosition(start + (needsComma ? 2 : 0) + templateJson.length);
				break;
			}
		}

		if (onchange) onchange(value);
	}

	function formatJSON() {
		try {
			const parsed = JSON.parse(value);
			const formatted = JSON.stringify(parsed, null, 2);

			// Only update if actually changed
			if (formatted !== value) {
				value = formatted;
				if (onchange) onchange(value);
				toastStore.success('JSON formatted successfully');
			} else {
				toastStore.info('JSON is already formatted');
			}
		} catch (e) {
			// Show error message to user
			toastStore.error('Invalid JSON: Cannot format');
		}
	}
</script>

<div class="grid grid-cols-1 lg:grid-cols-5 2xl:grid-cols-5 gap-6">
	<!-- Editor -->
	<div class="{showSidebar ? 'lg:col-span-2 2xl:col-span-2' : 'lg:col-span-5 2xl:col-span-5'}">
		<Card>
			<CardHeader>
				<div class="flex items-center justify-between">
					<CardTitle>Rule Condition Editor</CardTitle>
					<div class="flex gap-2">
						<Button
							type="button"
							variant="outline"
							size="sm"
							onclick={formatJSON}
							title="Format JSON (Ctrl+Shift+F)"
						>
							Format
						</Button>
						<Button
							variant="outline"
							size="sm"
							onclick={() => (showSidebar = !showSidebar)}
						>
							{showSidebar ? 'Hide' : 'Show'} Help
						</Button>
					</div>
				</div>
			</CardHeader>
			<CardContent>
				<textarea
					bind:this={textareaEl}
					bind:value
					oninput={() => onchange?.(value)}
					class="w-full h-96 p-4 font-mono text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
					placeholder={`{
  "equals": {
    "field": "color"
  }
}`}
					spellcheck="false"
				></textarea>

				{#if schemaFields.length > 0}
					<div class="mt-4">
						<p class="text-sm font-medium mb-2">Available Fields:</p>
						<div class="flex flex-wrap gap-1">
							{#each schemaFields as field}
								<Badge variant="outline" class="text-xs">{field}</Badge>
							{/each}
						</div>
					</div>
				{/if}
			</CardContent>
		</Card>
	</div>

	<!-- Help Sidebar -->
	{#if showSidebar}
		<div class="lg:col-span-3">
			<Card class="h-full">
				<CardHeader>
					<!-- Tabs -->
					<div class="flex gap-2 mb-4 border-b">
						<button
							type="button"
							class="px-4 py-2 text-sm font-medium border-b-2 transition-colors {sidebarTab === 'operators'
								? 'border-primary text-primary'
								: 'border-transparent text-muted-foreground hover:text-foreground'}"
							onclick={() => (sidebarTab = 'operators')}
						>
							Operators
						</button>
						<button
							type="button"
							class="px-4 py-2 text-sm font-medium border-b-2 transition-colors {sidebarTab === 'templates'
								? 'border-primary text-primary'
								: 'border-transparent text-muted-foreground hover:text-foreground'}"
							onclick={() => (sidebarTab = 'templates')}
						>
							Templates
						</button>
					</div>

					{#if sidebarTab === 'operators'}
						<CardTitle>Operators</CardTitle>
						<div class="mt-4 space-y-3">
							<input
								type="text"
									bind:value={searchTerm}
								placeholder="Search operators..."
								class="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
							/>
							<select
									bind:value={selectedCategory}
								class="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
							>
								{#each categories as cat}
									<option value={cat.value}>{cat.label}</option>
								{/each}
							</select>
						</div>
					{:else}
						<CardTitle>Templates</CardTitle>
						<div class="mt-4">
							<select
									bind:value={selectedTemplateCategory}
								class="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
							>
								{#each templateCategories as cat}
									<option value={cat.value}>{cat.label}</option>
								{/each}
							</select>
						</div>
					{/if}
				</CardHeader>
				<CardContent>
					{#if sidebarTab === 'operators'}
						<div class="space-y-4 max-h-[600px] overflow-y-auto">
							{#each filteredOperators() as operator}
								<div class="p-3 border rounded-lg hover:bg-accent/50 transition-colors">
									<div class="flex items-start justify-between mb-2">
										<div class="flex items-center gap-2">
											<span class="text-lg" aria-hidden="true">{operator.icon}</span>
											<h4 class="font-medium text-sm">{operator.displayName}</h4>
										</div>
										<div class="flex gap-1">
											<Button
												variant="ghost"
												size="sm"
												onclick={() => insertOperator(operator, 'insert')}
												class="text-xs"
												title="Add to condition (smart insertion)"
											>
												Insert
											</Button>
											<Button
												variant="outline"
												size="sm"
												onclick={() => insertOperator(operator, 'replace')}
												class="text-xs"
												title="Replace current content"
											>
												Replace
											</Button>
										</div>
									</div>
									<p class="text-xs text-muted-foreground mb-2">{operator.description}</p>
									<div class="flex flex-wrap gap-1">
										{#each operator.parameters as param}
											<Badge variant={param.required ? 'default' : 'secondary'} class="text-xs">
												{param.name}
											</Badge>
										{/each}
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="space-y-4 max-h-[600px] overflow-y-auto">
							{#each filteredTemplates() as template}
								<div class="p-3 border rounded-lg hover:bg-accent/50 transition-colors">
									<div class="flex items-start justify-between mb-2">
										<div class="flex-1">
											<h4 class="font-medium text-sm">{template.name}</h4>
											<Badge
												variant={template.category === 'exclusion' ? 'destructive' : 'default'}
												class="text-xs mt-1"
											>
												{template.category}
											</Badge>
										</div>
										<div class="flex gap-1">
											<Button
												variant="ghost"
												size="sm"
												onclick={() => insertTemplate(template, 'insert')}
												class="text-xs"
												title="Add to condition (smart insertion)"
											>
												Insert
											</Button>
											<Button
												variant="outline"
												size="sm"
												onclick={() => insertTemplate(template, 'replace')}
												class="text-xs"
												title="Replace current content"
											>
												Replace
											</Button>
										</div>
									</div>
									<p class="text-xs text-muted-foreground">{template.description}</p>
								</div>
							{/each}
						</div>
					{/if}
				</CardContent>
			</Card>
		</div>
	{/if}
</div>
