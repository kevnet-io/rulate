<svelte:head>
	<title>Compatibility Matrix - Rulate</title>
</svelte:head>

<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { Catalog, RuleSet, EvaluationMatrix, ComparisonResult } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';

	let catalogs: Catalog[] = [];
	let rulesets: RuleSet[] = [];
	let selectedCatalog: string = '';
	let selectedRuleset: string = '';
	let matrix: EvaluationMatrix | null = null;
	let loading = false;
	let error: string | null = null;
	let selectedPair: ComparisonResult | null = null;
	let items: string[] = [];

	async function loadOptions() {
		try {
			const [catalogsData, rulesetsData] = await Promise.all([
				api.getCatalogs(),
				api.getRuleSets()
			]);
			catalogs = catalogsData;
			rulesets = rulesetsData;

			if (catalogs.length > 0) selectedCatalog = catalogs[0].name;
			if (rulesets.length > 0) selectedRuleset = rulesets[0].name;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load options';
		}
	}

	async function evaluateMatrix() {
		if (!selectedCatalog || !selectedRuleset) {
			error = 'Please select both a catalog and a ruleset';
			return;
		}

		try {
			loading = true;
			error = null;
			selectedPair = null;
			matrix = await api.evaluateMatrix(selectedCatalog, selectedRuleset);
			items = getUniqueItemIds();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to evaluate matrix';
		} finally {
			loading = false;
		}
	}

	function getResult(item1Id: string, item2Id: string): ComparisonResult | null {
		if (!matrix) return null;
		return (
			matrix.results.find(
				(r) =>
					(r.item1_id === item1Id && r.item2_id === item2Id) ||
					(r.item1_id === item2Id && r.item2_id === item1Id)
			) || null
		);
	}

	function getUniqueItemIds(): string[] {
		if (!matrix) return [];
		const ids = new Set<string>();
		matrix.results.forEach((r) => {
			ids.add(r.item1_id);
			ids.add(r.item2_id);
		});
		return Array.from(ids).sort();
	}

	onMount(loadOptions);
</script>

<div class="container mx-auto px-4 py-8">
	<div class="mb-8">
		<h1 class="text-4xl font-bold mb-2">Compatibility Matrix</h1>
		<p class="text-muted-foreground">Visualize compatibility between all items in a catalog</p>
	</div>

	<div class="space-y-6">
		<Card>
			<CardHeader>
				<CardTitle>Evaluation Settings</CardTitle>
				<CardDescription>Select a catalog and ruleset to evaluate</CardDescription>
			</CardHeader>
			<CardContent>
				<div class="grid gap-4 md:grid-cols-3">
					<div>
						<label for="catalog" class="block text-sm font-medium mb-2">Catalog</label>
						<select
							id="catalog"
							bind:value={selectedCatalog}
							class="w-full px-3 py-2 border rounded-md bg-background"
						>
							{#each catalogs as catalog}
								<option value={catalog.name}>{catalog.name}</option>
							{/each}
						</select>
					</div>

					<div>
						<label for="ruleset" class="block text-sm font-medium mb-2">RuleSet</label>
						<select
							id="ruleset"
							bind:value={selectedRuleset}
							class="w-full px-3 py-2 border rounded-md bg-background"
						>
							{#each rulesets as ruleset}
								<option value={ruleset.name}>{ruleset.name}</option>
							{/each}
						</select>
					</div>

					<div class="flex items-end">
						<Button onclick={evaluateMatrix} disabled={loading} class="w-full">
							{loading ? 'Evaluating...' : 'Evaluate Matrix'}
						</Button>
					</div>
				</div>

				{#if error}
					<div class="mt-4 p-3 bg-destructive/10 border border-destructive rounded-md">
						<p class="text-sm text-destructive">{error}</p>
					</div>
				{/if}
			</CardContent>
		</Card>

		{#if matrix}
			<Card>
				<CardHeader>
					<CardTitle>Results</CardTitle>
					<CardDescription>
						{matrix.total_comparisons} comparisons • {matrix.compatible_count} compatible •
						{(matrix.compatibility_rate * 100).toFixed(1)}% compatibility rate
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div class="overflow-auto">
						<table class="w-full border-collapse">
							<thead>
								<tr>
									<th class="border p-2 bg-muted sticky left-0 z-10"></th>
									{#each items as item}
										<th class="border p-2 bg-muted text-xs font-medium min-w-[100px] max-w-[150px]">
											<div class="truncate text-center">
												{item}
											</div>
										</th>
									{/each}
								</tr>
							</thead>
							<tbody>
								{#each items as item1}
									<tr>
										<th
											class="border p-2 bg-muted text-left text-xs font-medium sticky left-0 z-10 whitespace-nowrap"
										>
											{item1}
										</th>
										{#each items as item2}
											{@const result = getResult(item1, item2)}
											{@const isSame = item1 === item2}
											<td
												class="border p-2 text-center cursor-pointer hover:brightness-95 transition-all"
												class:bg-muted={isSame}
												class:bg-emerald-50={result?.compatible && !isSame}
												class:text-emerald-700={result?.compatible && !isSame}
												class:bg-rose-50={result && !result.compatible && !isSame}
												class:text-rose-700={result && !result.compatible && !isSame}
												onclick={() => {
													if (!isSame && result) selectedPair = result;
												}}
												role="button"
												tabindex="0"
											>
												{#if isSame}
													<span class="text-xs text-muted-foreground">-</span>
												{:else if result}
													<span class="text-sm font-bold">
														{result.compatible ? '✓' : '✗'}
													</span>
												{:else}
													<span class="text-xs text-muted-foreground">?</span>
												{/if}
											</td>
										{/each}
									</tr>
								{/each}
							</tbody>
						</table>
					</div>

					<div class="mt-4 flex items-center gap-4 text-sm">
						<div class="flex items-center gap-2">
							<div class="w-5 h-5 bg-emerald-50 border border-emerald-200 rounded flex items-center justify-center">
								<span class="text-emerald-700 text-xs font-bold">✓</span>
							</div>
							<span>Compatible</span>
						</div>
						<div class="flex items-center gap-2">
							<div class="w-5 h-5 bg-rose-50 border border-rose-200 rounded flex items-center justify-center">
								<span class="text-rose-700 text-xs font-bold">✗</span>
							</div>
							<span>Incompatible</span>
						</div>
						<div class="flex items-center gap-2">
							<div class="w-5 h-5 bg-muted border rounded flex items-center justify-center">
								<span class="text-muted-foreground text-xs">-</span>
							</div>
							<span>Same item</span>
						</div>
					</div>
				</CardContent>
			</Card>
		{/if}

		{#if selectedPair}
			<Card>
				<CardHeader>
					<div class="flex items-start justify-between">
						<div>
							<CardTitle>Comparison Details</CardTitle>
							<CardDescription>
								{selectedPair.item1_id} vs {selectedPair.item2_id}
							</CardDescription>
						</div>
						<Badge variant={selectedPair.compatible ? 'default' : 'destructive'}>
							{selectedPair.compatible ? 'Compatible' : 'Incompatible'}
						</Badge>
					</div>
				</CardHeader>
				<CardContent>
					<div class="space-y-3">
						{#each selectedPair.rules_evaluated as ruleEval}
							<div class="border rounded-lg p-3">
								<div class="flex items-start justify-between mb-1">
									<h4 class="font-semibold text-sm">{ruleEval.rule_name}</h4>
									<Badge variant={ruleEval.passed ? 'default' : 'destructive'} class="text-xs">
										{ruleEval.passed ? 'Passed' : 'Failed'}
									</Badge>
								</div>
								<p class="text-sm text-muted-foreground">{ruleEval.reason}</p>
							</div>
						{/each}
					</div>
					<div class="mt-4">
						<Button variant="outline" size="sm" onclick={() => (selectedPair = null)}>
							Close
						</Button>
					</div>
				</CardContent>
			</Card>
		{/if}
	</div>
</div>
