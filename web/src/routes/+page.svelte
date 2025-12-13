<svelte:head>
	<title>Rulate - Rule-based Comparison Engine</title>
</svelte:head>

<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { Schema, RuleSet, Catalog } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';

	let schemas = $state<Schema[]>([]);
	let rulesets = $state<RuleSet[]>([]);
	let catalogs = $state<Catalog[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const [schemasData, rulesetsData, catalogsData] = await Promise.all([
				api.getSchemas(),
				api.getRuleSets(),
				api.getCatalogs()
			]);
			schemas = schemasData;
			rulesets = rulesetsData;
			catalogs = catalogsData;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load data';
		} finally {
			loading = false;
		}
	});
</script>

<div class="container mx-auto px-4 py-8">
	<div class="mb-8">
		<h1 class="text-4xl font-bold mb-2">Rulate Dashboard</h1>
		<p class="text-muted-foreground">
			Manage schemas, rulesets, and catalogs for your compatibility engine
		</p>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
		</Card>
	{:else if loading}
		<div class="grid gap-6 md:grid-cols-3">
			{#each [1, 2, 3] as _}
				<Card>
					<CardHeader>
						<Skeleton class="h-6 w-32 mb-2" />
						<Skeleton class="h-4 w-48" />
					</CardHeader>
					<CardContent>
						<Skeleton class="h-16 w-full" />
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-6 md:grid-cols-3">
			<a href="/schemas">
				<Card class="hover:bg-accent transition-colors cursor-pointer">
					<CardHeader>
						<div class="flex items-center justify-between">
							<CardTitle>Schemas</CardTitle>
							<Badge variant="secondary">{schemas.length}</Badge>
						</div>
						<CardDescription>Define dimensions and validation rules</CardDescription>
					</CardHeader>
					<CardContent>
						{#if schemas.length === 0}
							<p class="text-sm text-muted-foreground">No schemas created yet</p>
						{:else}
							<div class="space-y-1">
								{#each schemas.slice(0, 3) as schema}
									<div class="text-sm">
										<span class="font-medium">{schema.name}</span>
										<span class="text-muted-foreground text-xs ml-2">v{schema.version}</span>
									</div>
								{/each}
								{#if schemas.length > 3}
									<p class="text-xs text-muted-foreground mt-2">
										+{schemas.length - 3} more
									</p>
								{/if}
							</div>
						{/if}
					</CardContent>
				</Card>
			</a>

			<a href="/rulesets">
				<Card class="hover:bg-accent transition-colors cursor-pointer">
					<CardHeader>
						<div class="flex items-center justify-between">
							<CardTitle>RuleSets</CardTitle>
							<Badge variant="secondary">{rulesets.length}</Badge>
						</div>
						<CardDescription>Compatibility rules and conditions</CardDescription>
					</CardHeader>
					<CardContent>
						{#if rulesets.length === 0}
							<p class="text-sm text-muted-foreground">No rulesets created yet</p>
						{:else}
							<div class="space-y-1">
								{#each rulesets.slice(0, 3) as ruleset}
									<div class="text-sm">
										<span class="font-medium">{ruleset.name}</span>
										<span class="text-muted-foreground text-xs ml-2"
											>{ruleset.rules.length} rules</span
										>
									</div>
								{/each}
								{#if rulesets.length > 3}
									<p class="text-xs text-muted-foreground mt-2">
										+{rulesets.length - 3} more
									</p>
								{/if}
							</div>
						{/if}
					</CardContent>
				</Card>
			</a>

			<a href="/catalogs">
				<Card class="hover:bg-accent transition-colors cursor-pointer">
					<CardHeader>
						<div class="flex items-center justify-between">
							<CardTitle>Catalogs</CardTitle>
							<Badge variant="secondary">{catalogs.length}</Badge>
						</div>
						<CardDescription>Collections of items to evaluate</CardDescription>
					</CardHeader>
					<CardContent>
						{#if catalogs.length === 0}
							<p class="text-sm text-muted-foreground">No catalogs created yet</p>
						{:else}
							<div class="space-y-1">
								{#each catalogs.slice(0, 3) as catalog}
									<div class="text-sm">
										<span class="font-medium">{catalog.name}</span>
										<span class="text-muted-foreground text-xs ml-2"
											>{catalog.description || 'No description'}</span
										>
									</div>
								{/each}
								{#if catalogs.length > 3}
									<p class="text-xs text-muted-foreground mt-2">
										+{catalogs.length - 3} more
									</p>
								{/if}
							</div>
						{/if}
					</CardContent>
				</Card>
			</a>
		</div>

		<div class="mt-8">
			<Card>
				<CardHeader>
					<CardTitle>Quick Actions</CardTitle>
					<CardDescription>Get started with Rulate</CardDescription>
				</CardHeader>
				<CardContent>
					<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
						<a
							href="/explore"
							class="p-4 border-2 border-primary rounded-lg hover:bg-accent transition-colors"
						>
							<h3 class="font-semibold mb-1">🔍 Explore Compatibility</h3>
							<p class="text-sm text-muted-foreground">
								Interactively explore item compatibility - click through connections
							</p>
						</a>
						<a
							href="/matrix"
							class="p-4 border rounded-lg hover:bg-accent transition-colors"
						>
							<h3 class="font-semibold mb-1">View Compatibility Matrix</h3>
							<p class="text-sm text-muted-foreground">
								See all pairwise compatibility in a grid
							</p>
						</a>
						<a
							href="/catalogs"
							class="p-4 border rounded-lg hover:bg-accent transition-colors"
						>
							<h3 class="font-semibold mb-1">Manage Catalogs</h3>
							<p class="text-sm text-muted-foreground">
								View and manage your item collections
							</p>
						</a>
						<a
							href="/schemas"
							class="p-4 border rounded-lg hover:bg-accent transition-colors"
						>
							<h3 class="font-semibold mb-1">Create a Schema</h3>
							<p class="text-sm text-muted-foreground">
								Define the structure and validation rules
							</p>
						</a>
						<a
							href="/rulesets"
							class="p-4 border rounded-lg hover:bg-accent transition-colors"
						>
							<h3 class="font-semibold mb-1">Build a RuleSet</h3>
							<p class="text-sm text-muted-foreground">
								Create compatibility rules for evaluation
							</p>
						</a>
					</div>
				</CardContent>
			</Card>
		</div>
	{/if}
</div>
