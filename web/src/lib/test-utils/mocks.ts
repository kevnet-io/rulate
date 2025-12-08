/**
 * Test mocks for API client and SvelteKit features
 * Provides mock implementations of API methods and stores for testing
 */

import { vi } from 'vitest';
import { readable, writable } from 'svelte/store';
import type { Page } from '@sveltejs/kit';
import type * as ApiClient from '$lib/api/client';

/**
 * Create a mock $page store with default values
 * @param overrides Properties to override in the mock page
 * @returns Svelte readable store containing mock page data
 */
export function createMockPage(
	overrides?: Partial<Page>
): ReturnType<typeof readable<Page>> {
	return readable({
		url: new URL('http://localhost:5173/'),
		params: {},
		route: { id: null },
		status: 200,
		error: null,
		data: {},
		state: {},
		form: undefined,
		...overrides
	} as Page);
}

/**
 * Create a mock page store for a specific route
 * @param pathname The URL pathname (e.g., '/catalogs/test')
 * @param params The route parameters (e.g., { name: 'test' })
 * @returns Svelte readable store with mocked page for that route
 */
export function createMockPageForRoute(
	pathname: string,
	params: Record<string, string> = {}
): ReturnType<typeof readable<Page>> {
	return createMockPage({
		url: new URL(`http://localhost:5173${pathname}`),
		params
	});
}

/**
 * Mock implementation of the goto function
 */
export const mockGoto = vi.fn();

/**
 * Create a complete mock API client with all methods stubbed
 * All methods return resolved promises by default
 * @returns Mock API client object
 */
export function createMockApiClient(): Partial<typeof ApiClient.api> {
	return {
		// Schema endpoints
		getSchemas: vi.fn().mockResolvedValue([]),
		getSchema: vi.fn().mockResolvedValue({}),
		createSchema: vi.fn().mockResolvedValue({}),
		updateSchema: vi.fn().mockResolvedValue({}),
		deleteSchema: vi.fn().mockResolvedValue({}),

		// RuleSet endpoints
		getRuleSets: vi.fn().mockResolvedValue([]),
		getRuleSet: vi.fn().mockResolvedValue({}),
		createRuleSet: vi.fn().mockResolvedValue({}),
		updateRuleSet: vi.fn().mockResolvedValue({}),
		deleteRuleSet: vi.fn().mockResolvedValue({}),

		// Catalog endpoints
		getCatalogs: vi.fn().mockResolvedValue([]),
		getCatalog: vi.fn().mockResolvedValue({}),
		createCatalog: vi.fn().mockResolvedValue({}),
		updateCatalog: vi.fn().mockResolvedValue({}),
		deleteCatalog: vi.fn().mockResolvedValue({}),

		// Item endpoints
		getItems: vi.fn().mockResolvedValue([]),
		getItem: vi.fn().mockResolvedValue({}),
		createItem: vi.fn().mockResolvedValue({}),
		updateItem: vi.fn().mockResolvedValue({}),
		deleteItem: vi.fn().mockResolvedValue({}),

		// ClusterRuleSet endpoints
		getClusterRuleSets: vi.fn().mockResolvedValue([]),
		getClusterRuleSet: vi.fn().mockResolvedValue({}),
		createClusterRuleSet: vi.fn().mockResolvedValue({}),
		updateClusterRuleSet: vi.fn().mockResolvedValue({}),
		deleteClusterRuleSet: vi.fn().mockResolvedValue({}),

		// Evaluation endpoints
		evaluatePair: vi.fn().mockResolvedValue({}),
		evaluateMatrix: vi.fn().mockResolvedValue([]),
		evaluateItem: vi.fn().mockResolvedValue([]),
		evaluateClusters: vi.fn().mockResolvedValue({}),

		// Import/Export endpoints
		exportSchemas: vi.fn().mockResolvedValue({}),
		exportSchema: vi.fn().mockResolvedValue({}),
		exportRuleSets: vi.fn().mockResolvedValue({}),
		exportRuleSet: vi.fn().mockResolvedValue({}),
		exportClusterRuleSets: vi.fn().mockResolvedValue({}),
		exportClusterRuleSet: vi.fn().mockResolvedValue({}),
		exportCatalogs: vi.fn().mockResolvedValue({}),
		exportCatalog: vi.fn().mockResolvedValue({}),
		exportAll: vi.fn().mockResolvedValue({}),
		importSchemas: vi.fn().mockResolvedValue({}),
		importRuleSets: vi.fn().mockResolvedValue({}),
		importClusterRuleSets: vi.fn().mockResolvedValue({}),
		importCatalogs: vi.fn().mockResolvedValue({}),
		importAll: vi.fn().mockResolvedValue({})
	};
}

/**
 * Helper to set up API client mocks with vitest spies
 * @param mockData Object mapping method names to mock return values
 * @returns Object with spy functions for each method
 */
export function setupApiMocks(
	mockData: Partial<Record<keyof typeof ApiClient.api, any>>
): Record<string, any> {
	const mocks: Record<string, any> = {};

	for (const [method, value] of Object.entries(mockData)) {
		const spy = vi.spyOn(ApiClient.api, method as any);
		if (value instanceof Promise) {
			spy.mockReturnValue(value);
		} else {
			spy.mockResolvedValue(value);
		}
		mocks[method] = spy;
	}

	return mocks;
}

/**
 * Create a mock fetch function for API testing
 * @param responses Map of URL patterns to mock responses
 * @returns Mock fetch function that matches URLs and returns responses
 */
export function createMockFetch(responses: Record<string, any> = {}) {
	return vi.fn(async (url: string | Request) => {
		const urlString = typeof url === 'string' ? url : url.url;

		// Find matching response
		for (const [pattern, response] of Object.entries(responses)) {
			if (urlString.includes(pattern)) {
				if (response instanceof Error) {
					throw response;
				}
				return new Response(JSON.stringify(response), {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				});
			}
		}

		// Default: return 404
		return new Response(JSON.stringify({ error: 'Not found' }), {
			status: 404,
			headers: { 'Content-Type': 'application/json' }
		});
	});
}

/**
 * Helper to create a successful fetch response
 * @param data The response data
 * @param status HTTP status code (default 200)
 * @returns Response object
 */
export function createFetchResponse(data: any, status = 200) {
	return new Response(JSON.stringify(data), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

/**
 * Helper to create a failed fetch response
 * @param error Error message or object
 * @param status HTTP status code (default 400)
 * @returns Response object
 */
export function createFetchErrorResponse(error: any, status = 400) {
	return new Response(
		JSON.stringify(typeof error === 'string' ? { error } : error),
		{
			status,
			headers: { 'Content-Type': 'application/json' }
		}
	);
}

/**
 * Create a mock writable store for testing component state
 * @param initialValue Initial value of the store
 * @returns Writable store
 */
export function createMockStore<T>(initialValue: T) {
	return writable(initialValue);
}

/**
 * Setup common mocks for page tests (all in one call)
 * @returns Object containing all common mocks
 */
export function setupPageMocks() {
	const page = createMockPage();
	const api = createMockApiClient();
	const goto = mockGoto;

	return {
		page,
		api,
		goto
	};
}

/**
 * Helper to wait for a condition to be true (for async testing)
 * @param condition Function that returns boolean
 * @param timeout Maximum time to wait in ms
 * @param interval Time between checks in ms
 * @returns Promise that resolves when condition is true
 */
export async function waitFor(
	condition: () => boolean,
	timeout = 1000,
	interval = 50
): Promise<void> {
	const start = Date.now();
	while (!condition()) {
		if (Date.now() - start > timeout) {
			throw new Error('waitFor timeout exceeded');
		}
		await new Promise((resolve) => setTimeout(resolve, interval));
	}
}

/**
 * Create a rejected promise for error testing
 * @param error Error to reject with
 * @returns Promise that rejects with the error
 */
export function createRejectedPromise(error: Error) {
	return Promise.reject(error);
}

/**
 * Create a resolved promise for mocking
 * @param value Value to resolve with
 * @returns Promise that resolves with the value
 */
export function createResolvedPromise<T>(value: T) {
	return Promise.resolve(value);
}
