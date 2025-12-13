<svelte:head>
	<title>Catalogs - Rulate</title>
</svelte:head>

<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { Catalog } from '$lib/api/client';
	import { toastStore } from '$lib/stores/toast.svelte';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';
	import ConfirmModal from '$lib/components/ui/ConfirmModal.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';

	let catalogs = $state<Catalog[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let showDeleteModal = $state(false);
	let catalogToDelete = $state<string | null>(null);

	async function loadCatalogs() {
		try {
			loading = true;
			error = null;
			catalogs = await api.getCatalogs();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load catalogs';
			toastStore.error(error);
		} finally {
			loading = false;
		}
	}

	function confirmDelete(name: string) {
		catalogToDelete = name;
		showDeleteModal = true;
	}

	async function deleteCatalog() {
		if (!catalogToDelete) return;

		try {
			await api.deleteCatalog(catalogToDelete);
			toastStore.success(`Catalog "${catalogToDelete}" deleted successfully`);
			await loadCatalogs();
		} catch (err) {
			const errorMsg = err instanceof Error ? err.message : 'Failed to delete catalog';
			toastStore.error(errorMsg);
		}
	}

	onMount(loadCatalogs);
</script>

<div class="container mx-auto px-4 py-8">
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-4xl font-bold mb-2">Catalogs</h1>
			<p class="text-muted-foreground">Collections of items to evaluate</p>
		</div>
		<Button href="/catalogs/new">Create Catalog</Button>
	</div>

	{#if error}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>Error</CardTitle>
				<CardDescription>{error}</CardDescription>
			</CardHeader>
			<CardContent>
				<Button onclick={loadCatalogs}>Retry</Button>
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
	{:else if catalogs.length === 0}
		<EmptyState
			title="No Catalogs"
			description="Create your first catalog to organize and manage your items"
			actionText="Create Catalog"
			actionHref="/catalogs/new"
			icon="📚"
		/>
	{:else}
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each catalogs as catalog}
				<Card>
					<CardHeader>
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<CardTitle>{catalog.name}</CardTitle>
								<CardDescription>
									{catalog.description || 'No description'}
								</CardDescription>
							</div>
						</div>
					</CardHeader>
					<CardContent>
						<div class="space-y-3">
							<div>
								<p class="text-sm text-muted-foreground">
									Schema: <span class="font-medium text-foreground">{catalog.schema_name}</span>
								</p>
							</div>

							{#if catalog.created_at}
								<p class="text-xs text-muted-foreground">
									Created {new Date(catalog.created_at).toLocaleDateString()}
								</p>
							{/if}

							<div class="flex gap-2 pt-2">
								<Button href="/catalogs/{catalog.name}" variant="outline" size="sm"
									>View Items</Button
								>
								<Button
									variant="destructive"
									size="sm"
									onclick={() => confirmDelete(catalog.name)}>Delete</Button
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
	onConfirm={deleteCatalog}
	title="Delete Catalog"
	message="Are you sure you want to delete this catalog? This action cannot be undone."
	confirmText="Delete"
	isDanger={true}
	details={catalogToDelete ? { Name: catalogToDelete } : undefined}
/>
