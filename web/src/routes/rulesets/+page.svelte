<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { RuleSet } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';

	let rulesets: RuleSet[] = [];
	let loading = true;
	let error: string | null = null;

	async function loadRuleSets() {
		try {
			loading = true;
			error = null;
			rulesets = await api.getRuleSets();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load rulesets';
		} finally {
			loading = false;
		}
	}

	async function deleteRuleSet(name: string) {
		if (!confirm(`Are you sure you want to delete ruleset "${name}"?`)) {
			return;
		}

		try {
			await api.deleteRuleSet(name);
			await loadRuleSets();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to delete ruleset';
		}
	}

	onMount(loadRuleSets);
</script>

<div class="container mx-auto px-4 py-8">
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-4xl font-bold mb-2">RuleSets</h1>
			<p class="text-muted-foreground">Define compatibility rules and conditions</p>
		</div>
		<Button href="/rulesets/new">Create RuleSet</Button>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
			<CardContent>
				<Button onclick={loadRuleSets}>Retry</Button>
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
	{:else if rulesets.length === 0}
		<Card>
			<CardHeader>
				<CardTitle>No RuleSets</CardTitle>
				<CardDescription>Create your first ruleset to get started</CardDescription>
			</CardHeader>
			<CardContent>
				<Button href="/rulesets/new">Create RuleSet</Button>
			</CardContent>
		</Card>
	{:else}
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each rulesets as ruleset}
				<Card>
					<CardHeader>
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<CardTitle>{ruleset.name}</CardTitle>
								<CardDescription>Version {ruleset.version}</CardDescription>
							</div>
							<Badge variant="secondary">{ruleset.rules.length} rules</Badge>
						</div>
					</CardHeader>
					<CardContent>
						<div class="space-y-3">
							<div>
								<p class="text-sm text-muted-foreground mb-2">
									Schema: <span class="font-medium text-foreground">{ruleset.schema_name}</span>
								</p>
							</div>

							<div>
								<h4 class="text-sm font-medium mb-2">Rules</h4>
								{#if ruleset.rules.length === 0}
									<p class="text-sm text-muted-foreground">No rules defined</p>
								{:else}
									<div class="space-y-1">
										{#each ruleset.rules.slice(0, 3) as rule}
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
										{#if ruleset.rules.length > 3}
											<p class="text-xs text-muted-foreground">
												+{ruleset.rules.length - 3} more
											</p>
										{/if}
									</div>
								{/if}
							</div>

							{#if ruleset.created_at}
								<p class="text-xs text-muted-foreground">
									Created {new Date(ruleset.created_at).toLocaleDateString()}
								</p>
							{/if}

							<div class="flex gap-2 pt-2">
								<Button href="/rulesets/{ruleset.name}" variant="outline" size="sm"
									>View Details</Button
								>
								<Button
									variant="destructive"
									size="sm"
									onclick={() => deleteRuleSet(ruleset.name)}>Delete</Button
								>
							</div>
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>
