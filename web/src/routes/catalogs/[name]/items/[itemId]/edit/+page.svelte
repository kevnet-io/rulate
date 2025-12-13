<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import type { Catalog, Schema, Dimension, Item } from '$lib/api/client';
	import Card from '$lib/components/ui/card/card.svelte';
	import CardHeader from '$lib/components/ui/card/card-header.svelte';
	import CardTitle from '$lib/components/ui/card/card-title.svelte';
	import CardDescription from '$lib/components/ui/card/card-description.svelte';
	import CardContent from '$lib/components/ui/card/card-content.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Badge from '$lib/components/ui/badge/badge.svelte';

	let catalogName = $derived($page.params.name);
	let itemId = $derived($page.params.itemId);
	let pageTitle = $derived(`Edit ${itemId} - ${catalogName} - Rulate`);

	let catalog = $state<Catalog | null>(null);
	let schema = $state<Schema | null>(null);
	let item = $state<Item | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let submitting = $state(false);

	let name = $state('');
	let attributes = $state<Record<string, any>>({});

	async function loadData() {
		try {
			loading = true;
			error = null;
			item = await api.getItem(catalogName, itemId);
			catalog = await api.getCatalog(catalogName);
			schema = await api.getSchema(catalog.schema_name);

			// Pre-populate form with existing values
			if (item) {
				name = item.name;
				attributes = { ...item.attributes };
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load item';
		} finally {
			loading = false;
		}
	}

	function updateAttribute(key: string, value: any, dimension: Dimension) {
		// Convert value based on dimension type
		if (dimension.type === 'integer') {
			attributes[key] = value === '' ? 0 : parseInt(value, 10);
		} else if (dimension.type === 'float') {
			attributes[key] = value === '' ? 0 : parseFloat(value);
		} else if (dimension.type === 'boolean') {
			attributes[key] = value;
		} else if (dimension.type === 'list') {
			// Parse comma-separated values
			const items = value
				.split(',')
				.map((v: string) => v.trim())
				.filter((v: string) => v);

			// Convert based on item_type
			if (dimension.item_type === 'integer') {
				attributes[key] = items.map((v: string) => parseInt(v, 10));
			} else if (dimension.item_type === 'float') {
				attributes[key] = items.map((v: string) => parseFloat(v));
			} else if (dimension.item_type === 'boolean') {
				attributes[key] = items.map((v: string) => v.toLowerCase() === 'true');
			} else {
				attributes[key] = items;
			}
		} else {
			attributes[key] = value;
		}

		// Trigger reactivity by reassigning the object
		attributes = attributes;
	}

	function getListValueAsString(key: string): string {
		const value = attributes[key];
		if (Array.isArray(value)) {
			return value.join(', ');
		}
		return '';
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();
		console.log('Form submitted!');
		console.log('Catalog:', catalogName, 'Item:', itemId);
		console.log('Name:', name);
		console.log('Attributes:', attributes);

		error = null;

		// Validate
		if (!name.trim()) {
			error = 'Item name is required';
			console.error('Validation failed: name is required');
			return;
		}

		// Validate required fields
		if (schema) {
			for (const dim of schema.dimensions) {
				if (dim.required) {
					const value = attributes[dim.name];
					if (
						value === undefined ||
						value === null ||
						value === '' ||
						(Array.isArray(value) && value.length === 0)
					) {
						error = `${dim.name} is required`;
						console.error(`Validation failed: ${dim.name} is required`);
						return;
					}
				}
			}
		}

		try {
			submitting = true;
			console.log('Calling API to update item...');
			const result = await api.updateItem(catalogName, itemId, {
				name: name.trim(),
				attributes
			});
			console.log('API response:', result);
			console.log('Navigating to item detail page...');
			goto(`/catalogs/${catalogName}/items/${itemId}`);
		} catch (err) {
			console.error('API error:', err);
			error = err instanceof Error ? err.message : 'Failed to update item';
			submitting = false;
		}
	}

	onMount(loadData);
</script>

<svelte:head>
	<title>{pageTitle}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-7xl">
	<div class="mb-6">
		<Button href="/catalogs/{catalogName}/items/{itemId}" variant="ghost" size="sm"
			>← Back to Item</Button
		>
	</div>

	<div class="mb-8">
		<h1 class="text-4xl font-bold mb-2">Edit Item</h1>
		<p class="text-muted-foreground">Update item in {catalogName}</p>
	</div>

	{#if loading}
		<Card>
			<CardContent class="pt-6">
				<p class="text-muted-foreground">Loading item...</p>
			</CardContent>
		</Card>
	{:else if catalog && schema && item}
		<form onsubmit={handleSubmit}>
			<div class="space-y-6">
				<!-- Basic Info -->
				<Card>
					<CardHeader>
						<CardTitle>Basic Information</CardTitle>
						<CardDescription>Item identification</CardDescription>
					</CardHeader>
					<CardContent>
						<div class="space-y-4">
							<div>
								<label for="item_id" class="block text-sm font-medium mb-2">Item ID</label>
								<input
									type="text"
									id="item_id"
									value={itemId}
									class="w-full px-3 py-2 border border-input rounded-md bg-muted text-muted-foreground"
									disabled
								/>
								<p class="text-xs text-muted-foreground mt-1">Item ID cannot be changed</p>
							</div>
							<div>
								<label for="name" class="block text-sm font-medium mb-2">Name</label>
								<input
									type="text"
									id="name"
									bind:value={name}
									class="w-full px-3 py-2 border border-input rounded-md bg-background"
									placeholder="e.g., Blue Cotton T-Shirt"
									required
								/>
							</div>
						</div>
					</CardContent>
				</Card>

				<!-- Attributes -->
				<Card>
					<CardHeader>
						<CardTitle>Attributes</CardTitle>
						<CardDescription>
							Define attributes based on the {schema.name} schema
						</CardDescription>
					</CardHeader>
					<CardContent>
						<div class="space-y-4">
							{#each schema.dimensions as dim}
								<div>
									<div class="flex items-center gap-2 mb-2">
										<label for={dim.name} class="block text-sm font-medium">
											{dim.name}
										</label>
										<Badge variant="outline" class="text-xs">{dim.type}</Badge>
										{#if dim.required}
											<Badge variant="destructive" class="text-xs">Required</Badge>
										{/if}
									</div>

									{#if dim.type === 'string'}
										<input
											type="text"
											id={dim.name}
											value={attributes[dim.name] || ''}
											oninput={(e) => updateAttribute(dim.name, e.currentTarget.value, dim)}
											class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
											required={dim.required}
										/>
									{:else if dim.type === 'integer'}
										<input
											type="number"
											id={dim.name}
											value={attributes[dim.name] ?? ''}
											step="1"
											min={dim.min}
											max={dim.max}
											oninput={(e) => updateAttribute(dim.name, e.currentTarget.value, dim)}
											class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
											required={dim.required}
										/>
										{#if dim.min !== undefined || dim.max !== undefined}
											<p class="text-xs text-muted-foreground mt-1">
												Range: {dim.min ?? '−∞'} to {dim.max ?? '∞'}
											</p>
										{/if}
									{:else if dim.type === 'float'}
										<input
											type="number"
											id={dim.name}
											value={attributes[dim.name] ?? ''}
											step="0.1"
											min={dim.min}
											max={dim.max}
											oninput={(e) => updateAttribute(dim.name, e.currentTarget.value, dim)}
											class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
											required={dim.required}
										/>
										{#if dim.min !== undefined || dim.max !== undefined}
											<p class="text-xs text-muted-foreground mt-1">
												Range: {dim.min ?? '−∞'} to {dim.max ?? '∞'}
											</p>
										{/if}
									{:else if dim.type === 'boolean'}
										<div class="flex items-center gap-2">
											<input
												type="checkbox"
												id={dim.name}
												checked={attributes[dim.name]}
												onchange={(e) =>
													updateAttribute(dim.name, e.currentTarget.checked, dim)}
												class="rounded border-input"
											/>
											<label for={dim.name} class="text-sm">
												{attributes[dim.name] ? 'Yes' : 'No'}
											</label>
										</div>
									{:else if dim.type === 'enum'}
										<select
											id={dim.name}
											value={attributes[dim.name]}
											onchange={(e) => updateAttribute(dim.name, e.currentTarget.value, dim)}
											class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
											required={dim.required}
										>
											{#if dim.values}
												{#each dim.values as value}
													<option {value}>{value}</option>
												{/each}
											{/if}
										</select>
									{:else if dim.type === 'list'}
										<input
											type="text"
											id={dim.name}
											value={getListValueAsString(dim.name)}
											oninput={(e) => updateAttribute(dim.name, e.currentTarget.value, dim)}
											class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
											placeholder="Comma-separated values"
											required={dim.required}
										/>
										<p class="text-xs text-muted-foreground mt-1">
											Enter values separated by commas. Item type: {dim.item_type || 'string'}
										</p>
									{/if}
								</div>
							{/each}
						</div>
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
						{submitting ? 'Saving...' : 'Save Changes'}
					</Button>
					<Button
						type="button"
						variant="outline"
						href="/catalogs/{catalogName}/items/{itemId}">Cancel</Button
					>
				</div>
			</div>
		</form>
	{/if}
</div>
