<svelte:head>
	<title>Schemas - Rulate</title>
</svelte:head>

<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { Schema } from '$lib/api/client';
	import { toastStore } from '$lib/stores/toast.svelte';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';
	import ConfirmModal from '$lib/components/ui/ConfirmModal.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';

	let schemas = $state<Schema[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let showDeleteModal = $state(false);
	let schemaToDelete = $state<string | null>(null);

	async function loadSchemas() {
		try {
			loading = true;
			error = null;
			schemas = await api.getSchemas();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load schemas';
			toastStore.error(error);
		} finally {
			loading = false;
		}
	}

	function confirmDelete(name: string) {
		schemaToDelete = name;
		showDeleteModal = true;
	}

	async function deleteSchema() {
		if (!schemaToDelete) return;

		try {
			await api.deleteSchema(schemaToDelete);
			toastStore.success(`Schema "${schemaToDelete}" deleted successfully`);
			await loadSchemas();
		} catch (err) {
			const errorMsg = err instanceof Error ? err.message : 'Failed to delete schema';
			toastStore.error(errorMsg);
		}
	}

	onMount(loadSchemas);
</script>

<div class="container mx-auto px-4 py-8">
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-4xl font-bold mb-2">Schemas</h1>
			<p class="text-muted-foreground">
				Define the structure and validation rules for your items
			</p>
		</div>
		<Button href="/schemas/new">Create Schema</Button>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
			<CardContent>
				<Button onclick={loadSchemas}>Retry</Button>
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
	{:else if schemas.length === 0}
		<EmptyState
			title="No Schemas"
			description="Create your first schema to define the structure and validation rules for your items"
			actionText="Create Schema"
			actionHref="/schemas/new"
			icon="📋"
		/>
	{:else}
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each schemas as schema}
				<Card>
					<CardHeader>
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<CardTitle>{schema.name}</CardTitle>
								<CardDescription>Version {schema.version}</CardDescription>
							</div>
							<Badge variant="secondary">{schema.dimensions.length} dimensions</Badge>
						</div>
					</CardHeader>
					<CardContent>
						<div class="space-y-3">
							<div>
								<h4 class="text-sm font-medium mb-2">Dimensions</h4>
								<div class="flex flex-wrap gap-1">
									{#each schema.dimensions.slice(0, 5) as dim}
										<Badge variant="outline" class="text-xs">
											{dim.name}
											<span class="text-muted-foreground ml-1">({dim.type})</span>
										</Badge>
									{/each}
									{#if schema.dimensions.length > 5}
										<Badge variant="outline" class="text-xs">
											+{schema.dimensions.length - 5} more
										</Badge>
									{/if}
								</div>
							</div>

							{#if schema.created_at}
								<p class="text-xs text-muted-foreground">
									Created {new Date(schema.created_at).toLocaleDateString()}
								</p>
							{/if}

							<div class="flex gap-2 pt-2">
								<Button href="/schemas/{schema.name}" variant="outline" size="sm"
									>View Details</Button
								>
								<Button
									variant="destructive"
									size="sm"
									onclick={() => confirmDelete(schema.name)}>Delete</Button
								>
							</div>
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>

<ConfirmModal
	bind:isOpen={showDeleteModal}
	onClose={() => (showDeleteModal = false)}
	onConfirm={deleteSchema}
	title="Delete Schema"
	message="Are you sure you want to delete this schema? This action cannot be undone."
	confirmText="Delete"
	isDanger={true}
	details={schemaToDelete ? { Name: schemaToDelete } : undefined}
/>
