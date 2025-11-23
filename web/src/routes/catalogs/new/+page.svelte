<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import type { Schema } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';

	let name = '';
	let schema_name = '';
	let description = '';
	let schemas: Schema[] = [];
	let error: string | null = null;
	let submitting = false;
	let loadingSchemas = true;

	async function loadSchemas() {
		try {
			schemas = await api.getSchemas();
			if (schemas.length > 0) {
				schema_name = schemas[0].name;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load schemas';
		} finally {
			loadingSchemas = false;
		}
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();
		console.log('Catalog form submitted!');
		console.log('Name:', name);
		console.log('Schema:', schema_name);
		console.log('Description:', description);

		error = null;

		// Validate
		if (!name.trim()) {
			error = 'Catalog name is required';
			console.error('Validation failed: name is required');
			return;
		}

		if (!schema_name) {
			error = 'Schema selection is required';
			console.error('Validation failed: schema not selected');
			return;
		}

		try {
			submitting = true;
			console.log('Calling API to create catalog...');
			const result = await api.createCatalog({
				name: name.trim(),
				schema_name,
				description: description.trim() || undefined
			});
			console.log('API response:', result);
			console.log('Navigating to catalog page...');
			goto(`/catalogs/${name.trim()}`);
		} catch (err) {
			console.error('API error:', err);
			error = err instanceof Error ? err.message : 'Failed to create catalog';
			submitting = false;
		}
	}

	onMount(loadSchemas);
</script>

<div class="container mx-auto px-4 py-8 max-w-4xl">
	<div class="mb-8">
		<h1 class="text-4xl font-bold mb-2">Create Catalog</h1>
		<p class="text-muted-foreground">Create a collection of items to evaluate</p>
	</div>

	{#if loadingSchemas}
		<Card>
			<CardContent class="pt-6">
				<p class="text-muted-foreground">Loading schemas...</p>
			</CardContent>
		</Card>
	{:else if schemas.length === 0}
		<Card class="border-destructive">
			<CardHeader>
				<CardTitle>No Schemas Available</CardTitle>
				<CardDescription>You need to create a schema before creating a catalog</CardDescription>
			</CardHeader>
			<CardContent>
				<Button href="/schemas/new">Create Schema</Button>
			</CardContent>
		</Card>
	{:else}
		<form onsubmit={handleSubmit}>
			<div class="space-y-6">
				<!-- Basic Info -->
				<Card>
					<CardHeader>
						<CardTitle>Catalog Information</CardTitle>
						<CardDescription>Basic details about your catalog</CardDescription>
					</CardHeader>
					<CardContent>
						<div class="space-y-4">
							<div>
								<label for="name" class="block text-sm font-medium mb-2">Name</label>
								<input
									type="text"
									id="name"
									bind:value={name}
									class="w-full px-3 py-2 border border-input rounded-md bg-background"
									placeholder="e.g., my_wardrobe"
									required
								/>
							</div>
							<div>
								<label for="schema" class="block text-sm font-medium mb-2">Schema</label>
								<select
									id="schema"
									bind:value={schema_name}
									class="w-full px-3 py-2 border border-input rounded-md bg-background"
									required
								>
									{#each schemas as schema}
										<option value={schema.name}>{schema.name} (v{schema.version})</option>
									{/each}
								</select>
								<p class="text-xs text-muted-foreground mt-1">
									Items in this catalog will be validated against the selected schema
								</p>
							</div>
							<div>
								<label for="description" class="block text-sm font-medium mb-2"
									>Description <span class="text-muted-foreground font-normal"
										>(optional)</span
									></label
								>
								<textarea
									id="description"
									bind:value={description}
									class="w-full px-3 py-2 border border-input rounded-md bg-background"
									rows="3"
									placeholder="A brief description of this catalog..."
								></textarea>
							</div>
						</div>
					</CardContent>
				</Card>

				<!-- Info -->
				<Card>
					<CardHeader>
						<CardTitle>Next Steps</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-sm text-muted-foreground">
							After creating the catalog, you'll be able to add items to it from the catalog
							detail page.
						</p>
					</CardContent>
				</Card>

				<!-- Error Display -->
				{#if error}
					<Card class="border-destructive">
						<CardContent class="pt-6">
							<p class="text-destructive">{error}</p>
						</CardContent>
					</Card>
				{/if}

				<!-- Actions -->
				<div class="flex gap-3">
					<Button type="submit" disabled={submitting}>
						{submitting ? 'Creating...' : 'Create Catalog'}
					</Button>
					<Button type="button" variant="outline" href="/catalogs">Cancel</Button>
				</div>
			</div>
		</form>
	{/if}
</div>
