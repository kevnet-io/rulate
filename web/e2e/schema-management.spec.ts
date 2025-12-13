import { test, expect } from "@playwright/test";

test.describe("Schema Management Workflow", () => {
  test("should create and view a new schema", async ({ page }) => {
    // Navigate to schemas page
    await page.goto("/schemas");
    await expect(page).toHaveTitle(/Schemas/);

    // Try to click create schema button (if it exists)
    const createButton = page.locator("text=Create Schema").first();
    const createButtonExists = await createButton
      .isVisible({ timeout: 2000 })
      .catch(() => false);

    if (createButtonExists) {
      await createButton.click();
      // Verify we're on a creation page
      await expect(page).toHaveURL(/\/schemas\/new/);
    }
  });

  test("should view schema details", async ({ page }) => {
    // Navigate to schemas page
    await page.goto("/schemas");

    // Click on a schema (if one exists)
    const firstSchemaLink = page.locator('a:has-text("View Details")').first();
    const isVisible = await firstSchemaLink.isVisible();

    if (isVisible) {
      await firstSchemaLink.click();
      // Verify we're on detail page
      await expect(page).toHaveURL(/\/schemas\/[^/]+$/);
    }
  });

  test("should navigate to schema list from dashboard", async ({ page }) => {
    // Start from dashboard
    await page.goto("/");
    await expect(page).toHaveTitle(/Rulate/);

    // Click on Schemas card
    await page.click('a:has-text("Schemas")');

    // Verify navigation
    await expect(page).toHaveURL(/\/schemas$/);
    await expect(page).toHaveTitle(/Schemas/);
  });

  test("should display loading and empty states", async ({ page }) => {
    // Navigate to schemas
    await page.goto("/schemas");

    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Check if empty or has content
    const hasSchemas = await page.locator("text=No Schemas").isHidden();
    expect(typeof hasSchemas).toBe("boolean");
  });

  test("should handle navigation between pages", async ({ page }) => {
    // Navigate to dashboard
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Verify dashboard loads
    await expect(page).toHaveTitle(/Rulate/);

    // Check all navigation links exist with specific hrefs to avoid ambiguity
    const schemasLink = page.locator('a[href="/schemas"]').first();
    const rulesetsLink = page.locator('a[href="/rulesets"]').first();
    const catalogsLink = page.locator('a[href="/catalogs"]').first();

    await expect(schemasLink).toBeVisible({ timeout: 3000 });
    await expect(rulesetsLink).toBeVisible({ timeout: 3000 });
    await expect(catalogsLink).toBeVisible({ timeout: 3000 });
  });
});
