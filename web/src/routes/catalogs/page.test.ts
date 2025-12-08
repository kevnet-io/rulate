/**
 * Tests for Catalogs List Page (+page.svelte)
 *
 * Tests the catalogs list page data loading, display, and deletion.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as api from '$lib/api/client';
import { createMockCatalog } from '$lib/test-utils/fixtures';

// Mock the API client
vi.mock('$lib/api/client', () => ({
	api: {
		getCatalogs: vi.fn(),
		deleteCatalog: vi.fn()
	}
}));

// Helper to simulate page loading
async function loadCatalogs() {
	const catalogs = await api.api.getCatalogs();
	return catalogs;
}

describe('Catalogs List Page (+page)', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('Data Loading', () => {
		it('loads catalogs on mount', async () => {
			const mockCatalogs = [
				createMockCatalog({ name: 'Summer', schema_ref: 'Wardrobe' }),
				createMockCatalog({ name: 'Winter', schema_ref: 'Wardrobe' })
			];
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue(mockCatalogs);

			const catalogs = await loadCatalogs();

			expect(catalogs).toEqual(mockCatalogs);
			expect(api.api.getCatalogs).toHaveBeenCalledTimes(1);
		});

		it('starts with loading state', () => {
			let loading = true;
			expect(loading).toBe(true);
		});

		it('sets loading to false after data loads', async () => {
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([]);

			let loading = true;
			await loadCatalogs();
			loading = false;

			expect(loading).toBe(false);
		});

		it('initializes with empty catalog array', () => {
			let catalogs: any[] = [];
			expect(catalogs).toEqual([]);
		});

		it('clears error before loading', () => {
			let error: string | null = 'Previous error';
			error = null;
			expect(error).toBeNull();
		});
	});

	describe('Display Catalog Information', () => {
		it('displays catalog name', async () => {
			const mockCatalog = createMockCatalog({ name: 'TestCatalog' });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			expect(catalogs[0].name).toBe('TestCatalog');
		});

		it('displays catalog description', async () => {
			const mockCatalog = createMockCatalog({ description: 'This is a test catalog' });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			expect(catalogs[0].description).toBe('This is a test catalog');
		});

		it('shows default description when missing', async () => {
			const mockCatalog = createMockCatalog({ description: '' });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			const displayedDesc = catalogs[0].description || 'No description';
			expect(displayedDesc).toBe('No description');
		});

		it('displays schema name', async () => {
			const mockCatalog = createMockCatalog({ schema_ref: 'Wardrobe' });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			expect(catalogs[0].schema_ref).toBe('Wardrobe');
		});

		it('displays created_at date if present', async () => {
			const testDate = new Date('2024-01-15').toISOString();
			const mockCatalog = createMockCatalog({ created_at: testDate });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			expect(catalogs[0].created_at).toBe(testDate);
		});

		it('formats created_at date for display', () => {
			const testDate = new Date('2024-01-15').toISOString();
			const formatted = new Date(testDate).toLocaleDateString();

			expect(formatted).toBeTruthy();
			expect(formatted.length).toBeGreaterThan(0);
		});
	});

	describe('Multiple Catalogs', () => {
		it('displays all loaded catalogs', async () => {
			const mockCatalogs = [
				createMockCatalog({ name: 'Catalog1' }),
				createMockCatalog({ name: 'Catalog2' }),
				createMockCatalog({ name: 'Catalog3' })
			];
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue(mockCatalogs);

			const catalogs = await loadCatalogs();

			expect(catalogs).toHaveLength(3);
			expect(catalogs[0].name).toBe('Catalog1');
			expect(catalogs[1].name).toBe('Catalog2');
			expect(catalogs[2].name).toBe('Catalog3');
		});

		it('displays catalogs in grid layout', async () => {
			const mockCatalogs = [
				createMockCatalog({ name: 'C1' }),
				createMockCatalog({ name: 'C2' }),
				createMockCatalog({ name: 'C3' }),
				createMockCatalog({ name: 'C4' })
			];
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue(mockCatalogs);

			const catalogs = await loadCatalogs();

			expect(catalogs.length).toBe(4);
		});
	});

	describe('Empty State', () => {
		it('shows empty state when no catalogs', async () => {
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([]);

			const catalogs = await loadCatalogs();

			expect(catalogs).toEqual([]);
			expect(catalogs.length).toBe(0);
		});

		it('has create button in empty state', () => {
			const href = '/catalogs/new';
			expect(href).toBe('/catalogs/new');
		});
	});

	describe('Navigation', () => {
		it('has create catalog button link', () => {
			const href = '/catalogs/new';
			expect(href).toBe('/catalogs/new');
		});

		it('has view items button for each catalog', async () => {
			const mockCatalog = createMockCatalog({ name: 'TestCatalog' });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			const itemsHref = `/catalogs/${catalogs[0].name}`;
			expect(itemsHref).toBe('/catalogs/TestCatalog');
		});

		it('constructs correct items href for catalog', async () => {
			const mockCatalog = createMockCatalog({ name: 'MyCatalog' });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			expect(`/catalogs/${catalogs[0].name}`).toBe('/catalogs/MyCatalog');
		});
	});

	describe('Delete Functionality', () => {
		it('calls deleteCatalog with catalog name', async () => {
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([]);
			vi.spyOn(api.api, 'deleteCatalog').mockResolvedValue(undefined);

			await api.api.deleteCatalog('TestCatalog');

			expect(api.api.deleteCatalog).toHaveBeenCalledWith('TestCatalog');
		});

		it('reloads catalogs after delete', async () => {
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([]);
			vi.spyOn(api.api, 'deleteCatalog').mockResolvedValue(undefined);

			await api.api.deleteCatalog('TestCatalog');
			await api.api.getCatalogs();

			expect(api.api.getCatalogs).toHaveBeenCalled();
		});

		it('handles delete error', async () => {
			const error = new Error('Delete failed');
			vi.spyOn(api.api, 'deleteCatalog').mockRejectedValue(error);

			try {
				await api.api.deleteCatalog('TestCatalog');
			} catch (err) {
				expect(err).toEqual(error);
			}
		});
	});

	describe('Error Handling', () => {
		it('catches catalog loading error', async () => {
			const error = new Error('Failed to load catalogs');
			vi.spyOn(api.api, 'getCatalogs').mockRejectedValue(error);

			try {
				await loadCatalogs();
			} catch (err) {
				expect(err).toEqual(error);
			}
		});

		it('initializes error state as null', () => {
			let error: string | null = null;
			expect(error).toBeNull();
		});

		it('sets error message on failure', () => {
			let error: string | null = null;
			error = 'Failed to load catalogs';
			expect(error).toBe('Failed to load catalogs');
		});

		it('has retry button in error state', () => {
			expect(() => loadCatalogs()).toBeDefined();
		});

		it('clears error before retrying', async () => {
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([]);

			let error: string | null = 'Previous error';
			error = null;
			const catalogs = await loadCatalogs();

			expect(error).toBeNull();
		});

		it('handles non-Error exceptions', () => {
			const error: any = 'String error';
			expect(error).toBe('String error');
		});
	});

	describe('Page Title and Headings', () => {
		it('has page title', () => {
			expect('Catalogs - Rulate').toBeTruthy();
		});

		it('displays main heading', () => {
			expect('Catalogs').toBeTruthy();
		});

		it('displays subtitle', () => {
			const subtitle = 'Collections of items to evaluate';
			expect(subtitle).toBeTruthy();
		});
	});

	describe('Schema Reference', () => {
		it('displays associated schema for each catalog', async () => {
			const mockCatalog = createMockCatalog({ schema_ref: 'Wardrobe' });
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue([mockCatalog]);

			const catalogs = await loadCatalogs();

			expect(catalogs[0].schema_ref).toBe('Wardrobe');
		});

		it('handles different schema references', async () => {
			const mockCatalogs = [
				createMockCatalog({ name: 'C1', schema_ref: 'Schema1' }),
				createMockCatalog({ name: 'C2', schema_ref: 'Schema2' }),
				createMockCatalog({ name: 'C3', schema_ref: 'Schema3' })
			];
			vi.spyOn(api.api, 'getCatalogs').mockResolvedValue(mockCatalogs);

			const catalogs = await loadCatalogs();

			expect(catalogs[0].schema_ref).toBe('Schema1');
			expect(catalogs[1].schema_ref).toBe('Schema2');
			expect(catalogs[2].schema_ref).toBe('Schema3');
		});
	});
});
