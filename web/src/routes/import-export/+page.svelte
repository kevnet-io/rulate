<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card';

	let loading = $state(false);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);

	// File upload states
	let fileInput: HTMLInputElement;
	let selectedFile = $state<File | null>(null);
	let importType = $state<'all' | 'schemas' | 'rulesets' | 'cluster-rulesets' | 'catalogs'>('all');
	let skipExisting = $state(true);

	// Export functions
	async function downloadJSON(data: any, filename: string) {
		const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = filename;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	}

	async function exportAll() {
		try {
			loading = true;
			error = null;
			success = null;
			const data = await api.exportAll();
			await downloadJSON(data, 'rulate-export-all.json');
			success = 'All data exported successfully';
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function exportSchemas() {
		try {
			loading = true;
			error = null;
			success = null;
			const data = await api.exportSchemas();
			await downloadJSON(data, 'rulate-schemas.json');
			success = 'Schemas exported successfully';
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function exportRuleSets() {
		try {
			loading = true;
			error = null;
			success = null;
			const data = await api.exportRuleSets();
			await downloadJSON(data, 'rulate-rulesets.json');
			success = 'RuleSets exported successfully';
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function exportClusterRuleSets() {
		try {
			loading = true;
			error = null;
			success = null;
			const data = await api.exportClusterRuleSets();
			await downloadJSON(data, 'rulate-cluster-rulesets.json');
			success = 'ClusterRuleSets exported successfully';
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function exportCatalogs() {
		try {
			loading = true;
			error = null;
			success = null;
			const data = await api.exportCatalogs();
			await downloadJSON(data, 'rulate-catalogs.json');
			success = 'Catalogs exported successfully';
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	// Import functions
	function handleFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files && input.files.length > 0) {
			selectedFile = input.files[0];
			error = null;
			success = null;
		}
	}

	async function importData() {
		if (!selectedFile) {
			error = 'Please select a file to import';
			return;
		}

		try {
			loading = true;
			error = null;
			success = null;

			const fileContent = await selectedFile.text();
			const data = JSON.parse(fileContent);

			let result;
			switch (importType) {
				case 'all':
					result = await api.importAll(data, skipExisting);
					break;
				case 'schemas':
					result = await api.importSchemas(Array.isArray(data) ? data : [data], skipExisting);
					break;
				case 'rulesets':
					result = await api.importRuleSets(Array.isArray(data) ? data : [data], skipExisting);
					break;
				case 'cluster-rulesets':
					result = await api.importClusterRuleSets(Array.isArray(data) ? data : [data], skipExisting);
					break;
				case 'catalogs':
					result = await api.importCatalogs(Array.isArray(data) ? data : [data], skipExisting);
					break;
			}

			success = result.message;
			if (result.detail) {
				error = result.detail;
			}

			// Clear the file input
			selectedFile = null;
			if (fileInput) {
				fileInput.value = '';
			}
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Import/Export - Rulate</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<div class="mb-6">
		<h1 class="text-3xl font-bold mb-2">Import/Export Data</h1>
		<p class="text-gray-600">
			Export your data to JSON files or import data from previously exported files.
		</p>
	</div>

	{#if error}
		<div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
			<strong>Error:</strong> {error}
		</div>
	{/if}

	{#if success}
		<div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
			<strong>Success:</strong> {success}
		</div>
	{/if}

	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Export Section -->
		<Card.Root>
			<Card.Header>
				<Card.Title>Export Data</Card.Title>
				<Card.Description>
					Download your data as JSON files. You can export all data at once or export specific data types.
				</Card.Description>
			</Card.Header>
			<Card.Content class="space-y-3">
				<Button
					onclick={exportAll}
					disabled={loading}
					variant="default"
					class="w-full"
				>
					{loading ? 'Exporting...' : 'Export All Data'}
				</Button>

				<div class="border-t pt-3">
					<p class="text-sm text-muted-foreground mb-3">Or export by type:</p>

					<div class="grid grid-cols-2 gap-2">
						<Button
							onclick={exportSchemas}
							disabled={loading}
							variant="secondary"
							class="w-full"
						>
							Schemas
						</Button>

						<Button
							onclick={exportRuleSets}
							disabled={loading}
							variant="secondary"
							class="w-full"
						>
							RuleSets
						</Button>

						<Button
							onclick={exportClusterRuleSets}
							disabled={loading}
							variant="secondary"
							class="w-full"
						>
							Cluster RuleSets
						</Button>

						<Button
							onclick={exportCatalogs}
							disabled={loading}
							variant="secondary"
							class="w-full"
						>
							Catalogs
						</Button>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<!-- Import Section -->
		<Card.Root>
			<Card.Header>
				<Card.Title>Import Data</Card.Title>
				<Card.Description>
					Upload a JSON file to import data into Rulate. The file should be in the same format as exported files.
				</Card.Description>
			</Card.Header>
			<Card.Content class="space-y-4">
				<div>
					<label for="import-type" class="block text-sm font-medium mb-2">
						Import Type
					</label>
					<select
						id="import-type"
						bind:value={importType}
						class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					>
						<option value="all">All Data</option>
						<option value="schemas">Schemas Only</option>
						<option value="rulesets">RuleSets Only</option>
						<option value="cluster-rulesets">Cluster RuleSets Only</option>
						<option value="catalogs">Catalogs Only</option>
					</select>
				</div>

				<div>
					<label for="file-upload" class="block text-sm font-medium mb-2">
						Select JSON File
					</label>
					<input
						bind:this={fileInput}
						id="file-upload"
						type="file"
						accept=".json"
						onchange={handleFileSelect}
						class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
					{#if selectedFile}
						<p class="text-sm text-muted-foreground mt-1">
							Selected: {selectedFile.name}
						</p>
					{/if}
				</div>

				<div class="flex items-center">
					<input
						id="skip-existing"
						type="checkbox"
						bind:checked={skipExisting}
						class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
					/>
					<label for="skip-existing" class="ml-2 text-sm">
						Skip existing items (don't overwrite)
					</label>
				</div>

				<Button
					onclick={importData}
					disabled={loading || !selectedFile}
					variant="default"
					class="w-full"
				>
					{loading ? 'Importing...' : 'Import Data'}
				</Button>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Info Section -->
	<div class="mt-8">
		<Card.Root>
			<Card.Header>
				<Card.Title>About Import/Export</Card.Title>
			</Card.Header>
			<Card.Content class="space-y-2 text-sm text-muted-foreground">
				<p>
					<strong class="text-foreground">Export:</strong> Creates JSON files containing your data. Use this to back up your data or transfer it between instances.
				</p>
				<p>
					<strong class="text-foreground">Import:</strong> Loads data from JSON files. The file format must match the exported format.
				</p>
				<p>
					<strong class="text-foreground">Skip Existing:</strong> When enabled, items with names that already exist will be skipped. When disabled, the import will fail if duplicates are found.
				</p>
				<p>
					<strong class="text-foreground">Dependencies:</strong> When importing, ensure dependencies are imported in order: Schemas → RuleSets → Cluster RuleSets → Catalogs. The "All Data" import handles this automatically.
				</p>
			</Card.Content>
		</Card.Root>
	</div>
</div>
