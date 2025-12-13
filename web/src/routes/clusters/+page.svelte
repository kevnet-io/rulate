<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { Catalog, RuleSet, ClusterAnalysis, Cluster, ClusterRelationship, Item } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';

	let catalogs = $state<Catalog[]>([]);
	let rulesets = $state<RuleSet[]>([]);
	let selectedCatalog = $state('');
	let selectedRuleset = $state('');
	let selectedClusterRuleset = $state('');
	let minClusterSize = $state(2);
	let maxClusters = $state<number | undefined>(undefined);
	let analysis = $state<ClusterAnalysis | null>(null);
	let catalogItems = $state<Item[]>([]);
	let loading = $state(false);
	let error = $state<string | null>(null);

	async function loadOptions() {
		try {
			const [catalogsData, rulesetsData] = await Promise.all([
				api.getCatalogs(),
				api.getRuleSets()
			]);
			catalogs = catalogsData;
			rulesets = rulesetsData;

			if (catalogs.length > 0) selectedCatalog = catalogs[0].name;
			if (rulesets.length > 0) {
				selectedRuleset = rulesets[0].name;
				// For now, we'll use the same ruleset name with "_cluster" suffix as placeholder
				// In production, you'd have a separate endpoint for cluster rulesets
				selectedClusterRuleset = rulesets[0].name.replace('_rules', '_cluster_rules');
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load options';
		}
	}

	async function evaluateClusters() {
		if (!selectedCatalog || !selectedRuleset || !selectedClusterRuleset) {
			error = 'Please select catalog, ruleset, and cluster ruleset';
			return;
		}

		try {
			loading = true;
			error = null;

			// Load catalog items for display
			catalogItems = await api.getItems(selectedCatalog);

			// Evaluate clusters
			analysis = await api.evaluateClusters(
				selectedCatalog,
				selectedRuleset,
				selectedClusterRuleset,
				minClusterSize,
				maxClusters
			);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to evaluate clusters';
			analysis = null;
		} finally {
			loading = false;
		}
	}

	function getItemName(itemId: string): string {
		const item = catalogItems.find(i => i.item_id === itemId);
		return item ? item.name : itemId;
	}

	function getClusterRelationships(clusterId: string): ClusterRelationship[] {
		if (!analysis) return [];
		return analysis.relationships.filter(
			r => r.cluster_id === clusterId
		);
	}

	function getRelatedCluster(clusterId: string): Cluster | undefined {
		return analysis?.clusters.find(c => c.id === clusterId);
	}

	function scrollToCluster(clusterId: string) {
		const element = document.getElementById(`cluster-${clusterId}`);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth', block: 'start' });
		}
	}

	onMount(loadOptions);
</script>

<svelte:head>
	<title>Cluster Analysis - Rulate</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<div class="mb-8">
		<h1 class="text-4xl font-bold mb-2">Cluster Analysis</h1>
		<p class="text-muted-foreground">Find compatible sets of items in your catalog</p>
	</div>

	<div class="space-y-6">
		<!-- Evaluation Settings Card -->
		<Card>
			<CardHeader>
				<CardTitle>Evaluation Settings</CardTitle>
				<CardDescription>Configure cluster finding parameters</CardDescription>
			</CardHeader>
			<CardContent>
				<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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
						<label for="ruleset" class="block text-sm font-medium mb-2">Pairwise RuleSet</label>
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

					<div>
						<label for="cluster-ruleset" class="block text-sm font-medium mb-2">Cluster RuleSet</label>
						<input
							id="cluster-ruleset"
							type="text"
							bind:value={selectedClusterRuleset}
							placeholder="e.g., wardrobe_cluster_rules_v1"
							class="w-full px-3 py-2 border rounded-md bg-background"
						/>
					</div>

					<div>
						<label for="min-size" class="block text-sm font-medium mb-2">Min Cluster Size</label>
						<input
							id="min-size"
							type="number"
							bind:value={minClusterSize}
							min="2"
							class="w-full px-3 py-2 border rounded-md bg-background"
						/>
					</div>
				</div>

				<div class="mt-4 flex items-center gap-4">
					<Button onclick={evaluateClusters} disabled={loading} class="w-auto">
						{loading ? 'Finding Clusters...' : 'Find Clusters'}
					</Button>

					<div class="flex items-center gap-2">
						<input
							id="max-clusters"
							type="checkbox"
							checked={maxClusters !== undefined}
							onchange={(e) => {
								const target = e.target as HTMLInputElement;
								maxClusters = target.checked ? 20 : undefined;
							}}
							class="w-4 h-4"
						/>
						<label for="max-clusters" class="text-sm">Limit to top 20 clusters</label>
					</div>
				</div>

				{#if error}
					<div class="mt-4 p-3 bg-destructive/10 border border-destructive rounded-md">
						<p class="text-sm text-destructive">{error}</p>
					</div>
				{/if}
			</CardContent>
		</Card>

		<!-- Results -->
		{#if analysis}
			<!-- Summary Stats Card -->
			<Card>
				<CardHeader>
					<CardTitle>Results Summary</CardTitle>
					<CardDescription>
						{analysis.catalog_name} × {analysis.cluster_ruleset_name}
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div class="grid grid-cols-2 md:grid-cols-5 gap-4">
						<div class="text-center">
							<div class="text-3xl font-bold text-primary">{analysis.total_clusters}</div>
							<div class="text-sm text-muted-foreground">Total Clusters</div>
						</div>
						<div class="text-center">
							<div class="text-3xl font-bold text-primary">{analysis.max_cluster_size}</div>
							<div class="text-sm text-muted-foreground">Max Size</div>
						</div>
						<div class="text-center">
							<div class="text-3xl font-bold text-primary">{analysis.avg_cluster_size.toFixed(1)}</div>
							<div class="text-sm text-muted-foreground">Avg Size</div>
						</div>
						<div class="text-center">
							<div class="text-3xl font-bold text-primary">{analysis.total_items_covered}</div>
							<div class="text-sm text-muted-foreground">Items Covered</div>
						</div>
						<div class="text-center">
							<div class="text-3xl font-bold text-primary">{analysis.relationships.length}</div>
							<div class="text-sm text-muted-foreground">Relationships</div>
						</div>
					</div>
				</CardContent>
			</Card>

			<!-- Cluster Cards -->
			<div class="space-y-4">
				<h2 class="text-2xl font-bold">
					Clusters
					{#if analysis.clusters.filter(c => c.is_maximum).length > 0}
						<span class="text-sm text-muted-foreground font-normal">
							({analysis.clusters.filter(c => c.is_maximum).length} maximum @ {analysis.max_cluster_size} items)
						</span>
					{/if}
				</h2>

				{#each analysis.clusters as cluster, index (cluster.id)}
					<Card id="cluster-{cluster.id}">
						<CardHeader>
							<div class="flex items-start justify-between">
								<div class="flex-1">
									<CardTitle class="flex items-center gap-2">
										Cluster #{index + 1}
										{#if cluster.is_maximum}
											<Badge variant="default">MAXIMUM</Badge>
										{/if}
										<Badge variant="outline">{cluster.size} items</Badge>
									</CardTitle>
									<CardDescription>ID: {cluster.id}</CardDescription>
								</div>
							</div>
						</CardHeader>
						<CardContent>
							<!-- Items List -->
							<div class="mb-4">
								<h4 class="font-semibold text-sm mb-2">Items:</h4>
								<div class="flex flex-wrap gap-2">
									{#each cluster.item_ids as itemId}
										<Badge variant="secondary">
											<a
												href="/catalogs/{analysis.catalog_name}/items/{itemId}"
												class="hover:underline"
											>
												{getItemName(itemId)}
											</a>
										</Badge>
									{/each}
								</div>
							</div>

							<!-- Rule Evaluations -->
							<div class="mb-4">
								<h4 class="font-semibold text-sm mb-2">
									Rules: {cluster.rule_evaluations.filter(r => r.passed).length}/{cluster.rule_evaluations.length} passed
								</h4>
								<div class="space-y-1">
									{#each cluster.rule_evaluations as ruleEval}
										<div class="flex items-start gap-2 text-sm">
											<Badge
												variant={ruleEval.passed ? 'default' : 'destructive'}
												class="text-xs"
											>
												{ruleEval.passed ? '✓' : '✗'}
											</Badge>
											<div class="flex-1">
												<span class="font-medium">{ruleEval.rule_name}</span>
												<span class="text-muted-foreground"> - {ruleEval.reason}</span>
											</div>
										</div>
									{/each}
								</div>
							</div>

							<!-- Relationships -->
							{@const rels = getClusterRelationships(cluster.id)}
							{#if rels.length > 0}
								<div>
									<h4 class="font-semibold text-sm mb-2">Relationships:</h4>
									<div class="space-y-1">
										{#each rels.slice(0, 5) as rel}
											{@const relatedCluster = getRelatedCluster(rel.related_cluster_id)}
											<div class="flex items-center gap-2 text-sm">
												<Badge variant="outline" class="text-xs">
													{rel.relationship_type}
												</Badge>
												{#if relatedCluster}
													<button
														type="button"
														onclick={() => scrollToCluster(rel.related_cluster_id)}
														class="text-primary hover:underline"
													>
														Cluster ({relatedCluster.size} items)
													</button>
													<span class="text-muted-foreground">
														- {rel.overlap_size} shared
													</span>
												{:else}
													<span class="text-muted-foreground">
														{rel.related_cluster_id.slice(0, 8)}... ({rel.overlap_size} shared)
													</span>
												{/if}
											</div>
										{/each}
										{#if rels.length > 5}
											<div class="text-sm text-muted-foreground">
												... and {rels.length - 5} more relationships
											</div>
										{/if}
									</div>
								</div>
							{/if}
						</CardContent>
					</Card>
				{/each}

				{#if analysis.clusters.length === 0}
					<Card>
						<CardContent class="py-8 text-center text-muted-foreground">
							No clusters found matching the criteria
						</CardContent>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</div>
