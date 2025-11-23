<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
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

	let clusterRuleset: ClusterRuleSet | null = null;
	let loading = true;
	let error: string | null = null;

	$: clusterRulesetName = $page.params.name;
	$: pageTitle = `${clusterRulesetName} - Cluster RuleSet - Rulate`;

	async function loadClusterRuleSet() {
		try {
			loading = true;
			error = null;
			clusterRuleset = await api.getClusterRuleSet(clusterRulesetName);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load cluster ruleset';
		} finally {
			loading = false;
		}
	}

	function formatCondition(condition: Record<string, any>, indent = 0): string {
		const spaces = '  '.repeat(indent);
		let result = '';

		for (const [key, value] of Object.entries(condition)) {
			if (Array.isArray(value)) {
				result += `${spaces}${key}:\n`;
				value.forEach((item) => {
					if (typeof item === 'object') {
						result += formatCondition(item, indent + 1);
					} else {
						result += `${spaces}  - ${item}\n`;
					}
				});
			} else if (typeof value === 'object' && value !== null) {
				result += `${spaces}${key}:\n${formatCondition(value, indent + 1)}`;
			} else {
				result += `${spaces}${key}: ${value}\n`;
			}
		}

		return result;
	}

	onMount(loadClusterRuleSet);
</script>

<svelte:head>
	<title>{pageTitle}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<div class="mb-6">
		<Button href="/cluster-rulesets" variant="ghost" size="sm">← Back to Cluster RuleSets</Button>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
			<CardContent>
				<Button onclick={loadClusterRuleSet}>Retry</Button>
			</CardContent>
		</Card>
	{:else if loading}
		<Card>
			<CardHeader>
				<Skeleton class="h-8 w-64 mb-2" />
				<Skeleton class="h-4 w-32" />
			</CardHeader>
			<CardContent>
				<Skeleton class="h-64 w-full" />
			</CardContent>
		</Card>
	{:else if clusterRuleset}
		<div class="space-y-6">
			<Card>
				<CardHeader>
					<div class="flex items-start justify-between">
						<div>
							<CardTitle class="text-3xl">{clusterRuleset.name}</CardTitle>
							<CardDescription>Version {clusterRuleset.version}</CardDescription>
						</div>
						<Badge variant="secondary">{clusterRuleset.rules.length} rules</Badge>
					</div>
				</CardHeader>
				<CardContent>
					<div class="space-y-2">
						{#if clusterRuleset.description}
							<p class="text-sm mb-3">{clusterRuleset.description}</p>
						{/if}

						<p class="text-sm">
							<span class="text-muted-foreground">Schema:</span>
							<a
								href="/schemas/{clusterRuleset.schema_name}"
								class="font-medium text-primary hover:underline ml-2"
							>
								{clusterRuleset.schema_name}
							</a>
						</p>

						<p class="text-sm">
							<span class="text-muted-foreground">Pairwise RuleSet:</span>
							<a
								href="/rulesets/{clusterRuleset.pairwise_ruleset_name}"
								class="font-medium text-primary hover:underline ml-2"
							>
								{clusterRuleset.pairwise_ruleset_name}
							</a>
						</p>

						{#if clusterRuleset.created_at}
							<p class="text-sm text-muted-foreground">
								Created {new Date(clusterRuleset.created_at).toLocaleString()}
							</p>
						{/if}
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>Cluster Rules</CardTitle>
					<CardDescription>Validation rules for compatible sets of items</CardDescription>
				</CardHeader>
				<CardContent>
					{#if clusterRuleset.rules.length === 0}
						<p class="text-muted-foreground">No rules defined in this cluster ruleset</p>
					{:else}
						<div class="space-y-4">
							{#each clusterRuleset.rules as rule}
								<div class="border rounded-lg p-4">
									<div class="flex items-start justify-between mb-3">
										<div>
											<h4 class="font-semibold mb-1">{rule.name}</h4>
											{#if rule.description}
												<p class="text-sm text-muted-foreground mb-2">{rule.description}</p>
											{/if}
											<div class="flex gap-2">
												<Badge variant={rule.type === 'exclusion' ? 'destructive' : 'default'}>
													{rule.type}
												</Badge>
												{#if rule.enabled !== undefined}
													<Badge variant={rule.enabled ? 'default' : 'secondary'}>
														{rule.enabled ? 'Enabled' : 'Disabled'}
													</Badge>
												{/if}
											</div>
										</div>
									</div>

									<div class="bg-muted/50 rounded p-3 mt-2">
										<p class="text-xs font-medium text-muted-foreground mb-1">Condition:</p>
										<pre
											class="text-xs font-mono whitespace-pre-wrap">{formatCondition(rule.condition)}</pre>
									</div>

									{#if rule.type === 'exclusion'}
										<p class="text-xs text-muted-foreground mt-2">
											Set is <strong>invalid</strong> as a cluster if this condition is TRUE
										</p>
									{:else}
										<p class="text-xs text-muted-foreground mt-2">
											Set forms a valid cluster <strong>only if</strong> this condition is TRUE
										</p>
									{/if}
								</div>
							{/each}
						</div>
					{/if}
				</CardContent>
			</Card>
		</div>
	{/if}
</div>
