<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
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

	let ruleset = $state<RuleSet | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let rulesetName = $derived($page.params.name);
	let pageTitle = $derived(`${rulesetName} - RuleSet - Rulate`);

	async function loadRuleSet() {
		try {
			loading = true;
			error = null;
			ruleset = await api.getRuleSet(rulesetName);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load ruleset';
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

	onMount(loadRuleSet);
</script>

<svelte:head>
	<title>{pageTitle}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<div class="mb-6">
		<Button href="/rulesets" variant="ghost" size="sm">← Back to RuleSets</Button>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
			<CardContent>
				<Button onclick={loadRuleSet}>Retry</Button>
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
	{:else if ruleset}
		<div class="space-y-6">
			<Card>
				<CardHeader>
					<div class="flex items-start justify-between">
						<div>
							<CardTitle class="text-3xl">{ruleset.name}</CardTitle>
							<CardDescription>Version {ruleset.version}</CardDescription>
						</div>
						<Badge variant="secondary">{ruleset.rules.length} rules</Badge>
					</div>
				</CardHeader>
				<CardContent>
					<div class="space-y-2">
						<p class="text-sm">
							<span class="text-muted-foreground">Schema:</span>
							<a
								href="/schemas/{ruleset.schema_name}"
								class="font-medium text-primary hover:underline ml-2"
							>
								{ruleset.schema_name}
							</a>
						</p>
						{#if ruleset.created_at}
							<p class="text-sm text-muted-foreground">
								Created {new Date(ruleset.created_at).toLocaleString()}
							</p>
						{/if}
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>Rules</CardTitle>
					<CardDescription>Compatibility conditions for item pairs</CardDescription>
				</CardHeader>
				<CardContent>
					{#if ruleset.rules.length === 0}
						<p class="text-muted-foreground">No rules defined in this ruleset</p>
					{:else}
						<div class="space-y-4">
							{#each ruleset.rules as rule}
								<div class="border rounded-lg p-4">
									<div class="flex items-start justify-between mb-3">
										<div>
											<h4 class="font-semibold mb-1">{rule.name}</h4>
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
											Items are <strong>incompatible</strong> if this condition is TRUE
										</p>
									{:else}
										<p class="text-xs text-muted-foreground mt-2">
											Items are compatible <strong>only if</strong> this condition is TRUE
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
