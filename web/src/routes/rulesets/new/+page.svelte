<svelte:head>
	<title>Create RuleSet - Rulate</title>
</svelte:head>

<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import type { Rule, Schema } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';

	let name = '';
	let version = '1.0.0';
	let schema_name = '';
	let rules: Rule[] = [];
	let schemas: Schema[] = [];
	let error: string | null = null;
	let submitting = false;
	let loadingSchemas = true;

	async function loadSchemas() {
		try {
			schemas = await api.getSchemas();
			if (schemas.length > 0) {
				schema_name = schemas[0].name;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load schemas';
		} finally {
			loadingSchemas = false;
		}
	}

	function addRule() {
		rules = [
			...rules,
			{
				name: '',
				type: 'exclusion',
				condition: {},
				enabled: true
			}
		];
	}

	function removeRule(index: number) {
		rules = rules.filter((_, i) => i !== index);
	}

	function updateRule(index: number, updates: Partial<Rule>) {
		rules = rules.map((rule, i) => (i === index ? { ...rule, ...updates } : rule));
	}

	function updateRuleCondition(index: number, value: string) {
		try {
			const condition = value.trim() ? JSON.parse(value) : {};
			updateRule(index, { condition });
		} catch (err) {
			// Invalid JSON, don't update
		}
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();
		console.log('RuleSet form submitted!');
		console.log('Name:', name);
		console.log('Version:', version);
		console.log('Schema:', schema_name);
		console.log('Rules:', rules);

		error = null;

		// Validate
		if (!name.trim()) {
			error = 'RuleSet name is required';
			console.error('Validation failed: name is required');
			return;
		}

		if (!schema_name) {
			error = 'Schema selection is required';
			console.error('Validation failed: schema not selected');
			return;
		}

		if (rules.length === 0) {
			error = 'At least one rule is required';
			console.error('Validation failed: no rules');
			return;
		}

		for (const rule of rules) {
			if (!rule.name.trim()) {
				error = 'All rules must have a name';
				console.error('Validation failed: rule missing name');
				return;
			}
		}

		try {
			submitting = true;
			console.log('Calling API to create ruleset...');
			const result = await api.createRuleSet({
				name: name.trim(),
				version: version.trim(),
				schema_name,
				rules
			});
			console.log('API response:', result);
			console.log('Navigating to ruleset detail page...');
			goto(`/rulesets/${name.trim()}`);
		} catch (err) {
			console.error('API error:', err);
			error = err instanceof Error ? err.message : 'Failed to create ruleset';
			submitting = false;
		}
	}

	onMount(loadSchemas);
</script>

<div class="container mx-auto px-4 py-8 max-w-4xl">
	<div class="mb-8">
		<h1 class="text-4xl font-bold mb-2">Create RuleSet</h1>
		<p class="text-muted-foreground">Define compatibility rules and conditions</p>
	</div>

	{#if loadingSchemas}
		<Card>
			<CardContent class="pt-6">
				<p class="text-muted-foreground">Loading schemas...</p>
			</CardContent>
		</Card>
	{:else if schemas.length === 0}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>No Schemas Available</CardTitle>
				<CardDescription>You need to create a schema before creating a ruleset</CardDescription>
			</CardHeader>
			<CardContent>
				<Button href="/schemas/new">Create Schema</Button>
			</CardContent>
		</Card>
	{:else}
		<form onsubmit={handleSubmit}>
			<div class="space-y-6">
				<!-- Basic Info -->
				<Card>
					<CardHeader>
						<CardTitle>Basic Information</CardTitle>
						<CardDescription>RuleSet name, version, and schema</CardDescription>
					</CardHeader>
					<CardContent>
						<div class="space-y-4">
							<div>
								<label for="name" class="block text-sm font-medium mb-2">Name</label>
								<input
									type="text"
									id="name"
									bind:value={name}
									class="w-full px-3 py-2 border border-input rounded-md bg-background"
									placeholder="e.g., wardrobe_rules"
									required
								/>
							</div>
							<div>
								<label for="version" class="block text-sm font-medium mb-2">Version</label>
								<input
									type="text"
									id="version"
									bind:value={version}
									class="w-full px-3 py-2 border border-input rounded-md bg-background"
									placeholder="1.0.0"
									required
								/>
							</div>
							<div>
								<label for="schema" class="block text-sm font-medium mb-2">Schema</label>
								<select
									id="schema"
									bind:value={schema_name}
									class="w-full px-3 py-2 border border-input rounded-md bg-background"
									required
								>
									{#each schemas as schema}
										<option value={schema.name}>{schema.name} (v{schema.version})</option>
									{/each}
								</select>
							</div>
						</div>
					</CardContent>
				</Card>

				<!-- Rules -->
				<Card>
					<CardHeader>
						<div class="flex items-start justify-between">
							<div>
								<CardTitle>Rules</CardTitle>
								<CardDescription>Define exclusion and requirement rules</CardDescription>
							</div>
							<Button type="button" onclick={addRule} size="sm">Add Rule</Button>
						</div>
					</CardHeader>
					<CardContent>
						{#if rules.length === 0}
							<div class="text-center py-8 text-muted-foreground">
								<p>No rules defined yet</p>
								<p class="text-sm mt-2">Click "Add Rule" to get started</p>
							</div>
						{:else}
							<div class="space-y-4">
								{#each rules as rule, index}
									<div class="border border-border rounded-lg p-4">
										<div class="flex items-start justify-between mb-4">
											<Badge
												variant={rule.type === 'exclusion' ? 'destructive' : 'default'}
											>
												Rule {index + 1}
											</Badge>
											<Button
												type="button"
												variant="destructive"
												size="sm"
												onclick={() => removeRule(index)}>Remove</Button
											>
										</div>

										<div class="space-y-4">
											<!-- Name -->
											<div>
												<label class="block text-sm font-medium mb-2">Name</label>
												<input
													type="text"
													bind:value={rule.name}
													onchange={(e) =>
														updateRule(index, { name: e.currentTarget.value })}
													class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
													placeholder="e.g., same_zone_different_layer"
													required
												/>
											</div>

											<!-- Type and Enabled -->
											<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
												<div>
													<label class="block text-sm font-medium mb-2">Type</label>
													<select
														bind:value={rule.type}
														onchange={(e) =>
															updateRule(index, {
																type: e.currentTarget.value as Rule['type']
															})}
														class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
													>
														<option value="exclusion">Exclusion</option>
														<option value="requirement">Requirement</option>
													</select>
												</div>

												<div class="flex items-center gap-2">
													<input
														type="checkbox"
														id="enabled-{index}"
														bind:checked={rule.enabled}
														onchange={(e) =>
															updateRule(index, { enabled: e.currentTarget.checked })}
														class="rounded border-input"
													/>
													<label for="enabled-{index}" class="text-sm font-medium"
														>Enabled</label
													>
												</div>
											</div>

											<!-- Condition -->
											<div>
												<label class="block text-sm font-medium mb-2">
													Condition (JSON)
													<span class="text-muted-foreground font-normal ml-2"
														>e.g., {`{"equals": {"field": "color"}}`}</span
													>
												</label>
												<textarea
													value={JSON.stringify(rule.condition, null, 2)}
													oninput={(e) =>
														updateRuleCondition(index, e.currentTarget.value)}
													class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm font-mono"
													rows="4"
													placeholder="{'{}'}"
												></textarea>
											</div>
										</div>
									</div>
								{/each}
							</div>
						{/if}
					</CardContent>
				</Card>

				<!-- Error Display -->
				{#if error}
					<Card class="border-destructive">
						<CardContent class="pt-6">
							<p class="text-destructive">{error}</p>
						</CardContent>
					</Card>
				{/if}

				<!-- Actions -->
				<div class="flex gap-3">
					<Button type="submit" disabled={submitting}>
						{submitting ? 'Creating...' : 'Create RuleSet'}
					</Button>
					<Button type="button" variant="outline" href="/rulesets">Cancel</Button>
				</div>
			</div>
		</form>
	{/if}
</div>
