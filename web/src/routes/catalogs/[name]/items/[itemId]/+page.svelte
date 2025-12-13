<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { api } from '$lib/api/client';
	import type { Item, Schema } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';

	let item = $state<Item | null>(null);
	let schema = $state<Schema | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let catalogName = $derived($page.params.name);
	let itemId = $derived($page.params.itemId);
	let pageTitle = $derived(`${itemId} - ${catalogName} - Rulate`);

	async function loadItem() {
		try {
			loading = true;
			error = null;
			item = await api.getItem(catalogName, itemId);
			const catalog = await api.getCatalog(catalogName);
			schema = await api.getSchema(catalog.schema_name);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load item';
		} finally {
			loading = false;
		}
	}

	function getDimensionInfo(key: string) {
		if (!schema) return null;
		return schema.dimensions.find((d) => d.name === key);
	}

	onMount(loadItem);
</script>

<svelte:head>
	<title>{pageTitle}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<div class="mb-6">
		<Button href="/catalogs/{catalogName}" variant="ghost" size="sm"
			>← Back to Catalog</Button
		>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
			<CardContent>
				<Button onclick={loadItem}>Retry</Button>
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
	{:else if item}
		<div class="space-y-6">
			<Card>
				<CardHeader>
					<div class="flex items-start justify-between">
						<div>
							<CardTitle class="text-3xl">{item.name}</CardTitle>
							<CardDescription>{item.item_id}</CardDescription>
						</div>
						<Button href="/catalogs/{catalogName}/items/{itemId}/edit">Edit Item</Button>
					</div>
				</CardHeader>
				<CardContent>
					{#if item.created_at}
						<p class="text-sm text-muted-foreground">
							Created {new Date(item.created_at).toLocaleString()}
						</p>
					{/if}
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>Attributes</CardTitle>
					<CardDescription>Field values for this item</CardDescription>
				</CardHeader>
				<CardContent>
					<div class="space-y-3">
						{#each Object.entries(item.attributes) as [key, value]}
							{@const dimension = getDimensionInfo(key)}
							<div class="border rounded-lg p-3">
								<div class="flex items-start justify-between mb-1">
									<div>
										<h4 class="font-semibold">{key}</h4>
										{#if dimension}
											<div class="flex gap-1 mt-1">
												<Badge variant="outline" class="text-xs">{dimension.type}</Badge>
												{#if dimension.required}
													<Badge variant="destructive" class="text-xs">Required</Badge>
												{/if}
											</div>
										{/if}
									</div>
								</div>
								<div class="mt-2">
									{#if Array.isArray(value)}
										<div class="flex flex-wrap gap-1">
											{#each value as v}
												<Badge variant="secondary">{v}</Badge>
											{/each}
										</div>
									{:else if typeof value === 'boolean'}
										<Badge variant={value ? 'default' : 'secondary'}>
											{value ? 'True' : 'False'}
										</Badge>
									{:else}
										<p class="text-sm">{value}</p>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				</CardContent>
			</Card>

			{#if item.metadata && Object.keys(item.metadata).length > 0}
				<Card>
					<CardHeader>
						<CardTitle>Metadata</CardTitle>
						<CardDescription>Additional information about this item</CardDescription>
					</CardHeader>
					<CardContent>
						<pre class="text-xs bg-muted p-3 rounded overflow-auto">{JSON.stringify(
								item.metadata,
								null,
								2
							)}</pre>
					</CardContent>
				</Card>
			{/if}
		</div>
	{/if}
</div>
