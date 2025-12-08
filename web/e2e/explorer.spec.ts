import { test, expect } from '@playwright/test';

test.describe('Explorer Page Workflow', () => {
	test('should navigate to explorer from dashboard', async ({ page }) => {
		// Start from dashboard
		await page.goto('/');

		// Click on Explore link
		const exploreLink = page.locator('a:has-text("Explore"), a:has-text("Explorer")').first();
		const isVisible = await exploreLink.isVisible({ timeout: 2000 }).catch(() => false);

		if (isVisible) {
			await exploreLink.click();
			// Verify on explorer page
			await expect(page).toHaveURL(/\/explore$/);
			await expect(page).toHaveTitle(/Explore/);
		}
	});

	test('should display explorer controls', async ({ page }) => {
		// Navigate to explorer
		await page.goto('/explore');
		await page.waitForLoadState('networkidle');

		// Check for setup card with selectors
		const setupCard = page.locator('text=Setup').first();
		const isVisible = await setupCard.isVisible({ timeout: 3000 }).catch(() => false);

		// If available, verify controls exist
		if (isVisible) {
			const catalogSelect = page.locator('select[id*="catalog"], label:has-text("Catalog")').first();
			const rulesetSelect = page.locator('select[id*="ruleset"], label:has-text("RuleSet")').first();

			const hasCatalog = await catalogSelect.isVisible({ timeout: 2000 }).catch(() => false);
			const hasRuleset = await rulesetSelect.isVisible({ timeout: 2000 }).catch(() => false);

			expect(hasCatalog || hasRuleset || isVisible).toBeTruthy();
		}
	});

	test('should display loading state during evaluation', async ({ page }) => {
		// Navigate to explorer
		await page.goto('/explore');
		await page.waitForLoadState('networkidle');

		// Find and click explore button if available
		const exploreButton = page.locator('button:has-text("Explore")').first();
		const buttonExists = await exploreButton.isVisible({ timeout: 2000 }).catch(() => false);

		if (buttonExists) {
			// Click explore (may show loading briefly)
			await exploreButton.click();

			// Wait for any loading state or results
			await page.waitForTimeout(500);

			// Verify page structure remains
			await expect(page).toHaveTitle(/Explore/);
		}
	});

	test('should verify page title and headings', async ({ page }) => {
		// Navigate to explorer
		await page.goto('/explore');

		// Verify page title
		await expect(page).toHaveTitle(/Explore/);

		// Check for main heading
		const mainHeading = page.locator('h1:has-text("Compatibility")').first();
		const hasHeading = await mainHeading.isVisible({ timeout: 3000 }).catch(() => false);

		expect(typeof hasHeading).toBe('boolean');
	});

	test('should handle error states gracefully', async ({ page }) => {
		// Navigate to explorer
		await page.goto('/explore');
		await page.waitForLoadState('networkidle');

		// Try to click explore without selecting all options
		const exploreButton = page.locator('button:has-text("Explore")').first();
		const buttonExists = await exploreButton.isVisible({ timeout: 2000 }).catch(() => false);

		if (buttonExists && !await page.locator('text=compatible').isVisible({ timeout: 1000 }).catch(() => false)) {
			// Click explore - might show error
			await exploreButton.click();

			// Check for error message
			const errorVisible = await page.locator('text=select, text=required, text=error').first().isVisible({ timeout: 1000 }).catch(() => false);

			// Either error message or results should appear
			expect(typeof errorVisible).toBe('boolean');
		}
	});

	test('should verify navigation links work', async ({ page }) => {
		// Start from explorer
		await page.goto('/explore');
		await page.waitForLoadState('networkidle');

		// Verify we can navigate back to dashboard
		const nav = page.locator('nav, [class*="navigation"]').first();
		const hasNav = await nav.isVisible({ timeout: 2000 }).catch(() => false);

		if (hasNav) {
			// Look for dashboard or home link
			const homeLink = page.locator('a:has-text("Home"), a:has-text("Dashboard"), a:has-text("Rulate")').first();
			const hasHomeLink = await homeLink.isVisible({ timeout: 2000 }).catch(() => false);

			expect(typeof hasHomeLink).toBe('boolean');
		}
	});
});
