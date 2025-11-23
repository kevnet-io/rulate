<svelte:head>
	<title>Cluster RuleSets - Rulate</title>
</svelte:head>

<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { ClusterRuleSet } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';

	let clusterRulesets: ClusterRuleSet[] = [];
	let loading = true;
	let error: string | null = null;

	async function loadClusterRuleSets() {
		try {
			loading = true;
			error = null;
			clusterRulesets = await api.getClusterRuleSets();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load cluster rulesets';
		} finally {
			loading = false;
		}
	}

	async function deleteClusterRuleSet(name: string) {
		if (!confirm(`Are you sure you want to delete cluster ruleset "${name}"?`)) {
			return;
		}

		try {
			await api.deleteClusterRuleSet(name);
			await loadClusterRuleSets();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to delete cluster ruleset';
		}
	}

	onMount(loadClusterRuleSets);
</script>

<div class="container mx-auto px-4 py-8">
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-4xl font-bold mb-2">Cluster RuleSets</h1>
			<p class="text-muted-foreground">Define cluster-level validation rules for compatible sets</p>
		</div>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
			<CardContent>
				<Button onclick={loadClusterRuleSets}>Retry</Button>
			</CardContent>
		</Card>
	{:else if loading}
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each [1, 2, 3] as _}
				<Card>
					<CardHeader>
						<Skeleton class="h-6 w-48 mb-2" />
						<Skeleton class="h-4 w-32" />
					</CardHeader>
					<CardContent>
						<Skeleton class="h-16 w-full" />
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else if clusterRulesets.length === 0}
		<Card>
			<CardHeader>
				<CardTitle>No Cluster RuleSets</CardTitle>
				<CardDescription>No cluster rulesets have been created yet</CardDescription>
			</CardHeader>
			<CardContent>
				<p class="text-sm text-muted-foreground">
					Cluster rulesets define validation rules for compatible sets of items. They work together with pairwise rulesets to determine which sets form valid clusters.
				</p>
			</CardContent>
		</Card>
	{:else}
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each clusterRulesets as clusterRuleset}
				<Card>
					<CardHeader>
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<CardTitle>{clusterRuleset.name}</CardTitle>
								<CardDescription>Version {clusterRuleset.version}</CardDescription>
							</div>
							<Badge variant="secondary">{clusterRuleset.rules.length} rules</Badge>
						</div>
					</CardHeader>
					<CardContent>
						<div class="space-y-3">
							<div>
								<p class="text-sm text-muted-foreground mb-1">
									Schema: <span class="font-medium text-foreground">{clusterRuleset.schema_name}</span>
								</p>
								<p class="text-sm text-muted-foreground mb-2">
									Pairwise: <span class="font-medium text-foreground">{clusterRuleset.pairwise_ruleset_name}</span>
								</p>
							</div>

							{#if clusterRuleset.description}
								<p class="text-sm text-muted-foreground">{clusterRuleset.description}</p>
							{/if}

							<div>
								<h4 class="text-sm font-medium mb-2">Rules</h4>
								{#if clusterRuleset.rules.length === 0}
									<p class="text-sm text-muted-foreground">No rules defined</p>
								{:else}
									<div class="space-y-1">
										{#each clusterRuleset.rules.slice(0, 3) as rule}
											<div class="flex items-center gap-2">
												<Badge
													variant={rule.type === 'exclusion' ? 'destructive' : 'default'}
													class="text-xs"
												>
													{rule.type}
												</Badge>
												<span class="text-sm truncate">{rule.name}</span>
											</div>
										{/each}
										{#if clusterRuleset.rules.length > 3}
											<p class="text-xs text-muted-foreground">
												+{clusterRuleset.rules.length - 3} more
											</p>
										{/if}
									</div>
								{/if}
							</div>

							{#if clusterRuleset.created_at}
								<p class="text-xs text-muted-foreground">
									Created {new Date(clusterRuleset.created_at).toLocaleDateString()}
								</p>
							{/if}

							<div class="flex gap-2 pt-2">
								<Button href="/cluster-rulesets/{clusterRuleset.name}" variant="outline" size="sm"
									>View Details</Button
								>
								<Button
									variant="destructive"
									size="sm"
									onclick={() => deleteClusterRuleSet(clusterRuleset.name)}>Delete</Button
								>
							</div>
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>
