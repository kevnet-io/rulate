/**
 * Custom render helpers for testing Svelte components
 * Wraps @testing-library/svelte render with common setup
 */

import { render as tlRender, type RenderResult } from '@testing-library/svelte';
import { readable } from 'svelte/store';
import { vi } from 'vitest';
import type { Page } from '@sveltejs/kit';
import { createMockPage, createMockPageForRoute } from './mocks';

interface RenderOptions {
	pageData?: Partial<Page>;
	props?: Record<string, any>;
	slots?: Record<string, any>;
}

/**
 * Render a component with mocked SvelteKit $page store
 * Automatically mocks $app/stores for the component
 * @param component The Svelte component to render
 * @param options Render options including pageData, props, and slots
 * @returns RenderResult from @testing-library/svelte
 */
export function renderWithPage(
	component: any,
	options: RenderOptions = {}
): RenderResult {
	const { pageData, props, slots } = options;

	// Create the page store with provided data
	const pageStore = pageData
		? createMockPage(pageData)
		: createMockPage();

	// Mock $app/stores before rendering
	vi.doMock('$app/stores', () => ({
		page: pageStore
	}));

	try {
		return tlRender(component, {
			props,
			slots
		});
	} finally {
		vi.doUnmock('$app/stores');
	}
}

/**
 * Render a component with mocked navigation
 * Automatically mocks $app/navigation for the component
 * @param component The Svelte component to render
 * @param options Render options
 * @returns RenderResult from @testing-library/svelte
 */
export function renderWithNavigation(
	component: any,
	options: RenderOptions = {}
): RenderResult {
	const { props, slots } = options;

	// Mock $app/navigation
	const gotoMock = vi.fn();
	vi.doMock('$app/navigation', () => ({
		goto: gotoMock
	}));

	try {
		return tlRender(component, {
			props,
			slots
		});
	} finally {
		vi.doUnmock('$app/navigation');
	}
}

/**
 * Render a component with both $page store and navigation mocked
 * @param component The Svelte component to render
 * @param options Render options
 * @returns RenderResult from @testing-library/svelte
 */
export function renderWithSvelteKit(
	component: any,
	options: RenderOptions = {}
): RenderResult {
	const { pageData, props, slots } = options;

	const pageStore = pageData
		? createMockPage(pageData)
		: createMockPage();

	const gotoMock = vi.fn();

	// Mock both stores
	vi.doMock('$app/stores', () => ({
		page: pageStore
	}));

	vi.doMock('$app/navigation', () => ({
		goto: gotoMock
	}));

	try {
		return tlRender(component, {
			props,
			slots
		});
	} finally {
		vi.doUnmock('$app/stores');
		vi.doUnmock('$app/navigation');
	}
}

/**
 * Render a component with page data for a specific route
 * @param component The Svelte component to render
 * @param pathname The URL pathname (e.g., '/catalogs/test')
 * @param params The route parameters
 * @param options Additional render options
 * @returns RenderResult from @testing-library/svelte
 */
export function renderPageComponent(
	component: any,
	pathname: string,
	params: Record<string, string> = {},
	options: Omit<RenderOptions, 'pageData'> = {}
): RenderResult {
	const pageStore = createMockPageForRoute(pathname, params);

	vi.doMock('$app/stores', () => ({
		page: pageStore
	}));

	try {
		return tlRender(component, {
			props: options.props,
			slots: options.slots
		});
	} finally {
		vi.doUnmock('$app/stores');
	}
}

/**
 * Render a component with provided props
 * Shorthand for common case
 * @param component The Svelte component to render
 * @param props Props to pass to the component
 * @returns RenderResult from @testing-library/svelte
 */
export function renderComponent(
	component: any,
	props: Record<string, any> = {}
): RenderResult {
	return tlRender(component, { props });
}

/**
 * Helper to get all elements matching a selector
 * @param container The container element (usually from render result)
 * @param selector CSS selector
 * @returns Array of matching elements
 */
export function querySelectorAll(
	container: HTMLElement,
	selector: string
): HTMLElement[] {
	return Array.from(container.querySelectorAll(selector)) as HTMLElement[];
}

/**
 * Helper to get single element matching a selector
 * @param container The container element
 * @param selector CSS selector
 * @returns Matching element or null
 */
export function querySelector(
	container: HTMLElement,
	selector: string
): HTMLElement | null {
	return container.querySelector(selector) as HTMLElement | null;
}

/**
 * Helper to check if element has a class
 * @param element The element to check
 * @param className The class name
 * @returns True if element has the class
 */
export function hasClass(element: HTMLElement, className: string): boolean {
	return element.classList.contains(className);
}

/**
 * Helper to get all classes on an element
 * @param element The element
 * @returns Array of class names
 */
export function getClasses(element: HTMLElement): string[] {
	return Array.from(element.classList);
}

/**
 * Helper to get computed style value
 * @param element The element
 * @param property CSS property name
 * @returns Computed style value
 */
export function getComputedStyle(element: HTMLElement, property: string): string {
	return window.getComputedStyle(element).getPropertyValue(property);
}

/**
 * Helper to wait for element to appear in DOM
 * @param container The container to search in
 * @param selector CSS selector for element to wait for
 * @param timeout Maximum time to wait in ms
 * @returns Promise that resolves with the element
 */
export async function waitForElement(
	container: HTMLElement,
	selector: string,
	timeout = 1000
): Promise<HTMLElement> {
	const start = Date.now();
	while (true) {
		const element = container.querySelector(selector);
		if (element) {
			return element as HTMLElement;
		}
		if (Date.now() - start > timeout) {
			throw new Error(`Element not found: ${selector}`);
		}
		await new Promise((resolve) => setTimeout(resolve, 50));
	}
}

/**
 * Helper to wait for element to disappear from DOM
 * @param container The container to search in
 * @param selector CSS selector for element to wait for
 * @param timeout Maximum time to wait in ms
 * @returns Promise that resolves when element is gone
 */
export async function waitForElementToDisappear(
	container: HTMLElement,
	selector: string,
	timeout = 1000
): Promise<void> {
	const start = Date.now();
	while (true) {
		const element = container.querySelector(selector);
		if (!element) {
			return;
		}
		if (Date.now() - start > timeout) {
			throw new Error(`Element still visible: ${selector}`);
		}
		await new Promise((resolve) => setTimeout(resolve, 50));
	}
}

/**
 * Re-export common utilities from @testing-library/svelte
 * for convenience
 */
export { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
export type { RenderResult } from '@testing-library/svelte';
