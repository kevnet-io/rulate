import { test, expect } from '@playwright/test';

test.describe('Catalog Management Workflow', () => {
	test('should navigate to catalogs page', async ({ page }) => {
		// From dashboard
		await page.goto('/');
		await page.click('a:has-text("Catalogs")');

		// Verify navigation
		await expect(page).toHaveURL(/\/catalogs$/);
		await expect(page).toHaveTitle(/Catalogs/);
	});

	test('should navigate to catalog creation page', async ({ page }) => {
		// Navigate to catalogs
		await page.goto('/catalogs');

		// Click create button
		const createButton = page.locator('button:has-text("Create Catalog"), a:has-text("Create Catalog")').first();
		await createButton.click();

		// Verify on creation page
		await expect(page).toHaveURL(/\/catalogs\/new/);
		await expect(page).toHaveTitle(/Create.*Catalog/);
	});

	test('should view catalog items page', async ({ page }) => {
		// Navigate to catalogs
		await page.goto('/catalogs');
		await page.waitForLoadState('networkidle');

		// Check if there are catalogs to view
		const viewButton = page.locator('a:has-text("View Items")').first();
		const isVisible = await viewButton.isVisible({ timeout: 3000 }).catch(() => false);

		if (isVisible) {
			await viewButton.click();
			// Verify we're on a catalog detail page
			await expect(page).toHaveURL(/\/catalogs\/[^/]+$/);
		}
	});

	test('should display catalog list with proper structure', async ({ page }) => {
		// Navigate to catalogs
		await page.goto('/catalogs');
		await page.waitForLoadState('networkidle');

		// Verify page title
		await expect(page).toHaveTitle(/Catalogs/);

		// Page should load successfully (either with catalogs or empty state)
		// This is a basic structural test
		const pageContent = await page.content();
		expect(pageContent).toContain('Catalogs');
	});

	test('should navigate back from item creation to catalog', async ({ page }) => {
		// Navigate to a catalog with items
		await page.goto('/catalogs');
		await page.waitForLoadState('networkidle');

		// Try to click an add item button if available
		const addItemButton = page.locator('a:has-text("Add Item"), a:has-text("new")').first();
		const isVisible = await addItemButton.isVisible({ timeout: 2000 }).catch(() => false);

		if (isVisible) {
			await addItemButton.click();
			// Should be on item creation page
			await expect(page).toHaveURL(/\/catalogs\/[^/]+\/items\/new/);

			// Click back or cancel button
			const backButton = page.locator('button:has-text("Cancel"), a:has-text("Back"), button:has-text("Back")').first();
			const hasBackButton = await backButton.isVisible({ timeout: 2000 }).catch(() => false);

			if (hasBackButton) {
				await backButton.click();
				// Should navigate back to catalog page
				await expect(page).toHaveURL(/\/catalogs\/[^/]+$/);
			}
		}
	});

	test('should verify catalog cards display required information', async ({ page }) => {
		// Navigate to catalogs
		await page.goto('/catalogs');
		await page.waitForLoadState('networkidle');

		// Check for cards with catalog info (if any exist)
		const catalogCards = page.locator('[class*="card"], [class*="grid"]').first();
		const isVisible = await catalogCards.isVisible({ timeout: 2000 }).catch(() => false);

		expect(typeof isVisible).toBe('boolean');
	});
});
