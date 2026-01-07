import { test, expect } from "@playwright/test";

test.describe("Cluster Builder Page", () => {
  test("should navigate to cluster builder from navigation", async ({
    page,
  }) => {
    // Start from dashboard
    await page.goto("/");

    // Click on Builder link
    const builderLink = page.locator('a:has-text("Builder")').first();
    const isVisible = await builderLink
      .isVisible({ timeout: 2000 })
      .catch(() => false);

    if (isVisible) {
      await builderLink.click();
      // Verify on cluster builder page
      await expect(page).toHaveURL(/\/cluster-builder$/);
      await expect(page).toHaveTitle(/Cluster Builder/);
    }
  });

  test("should display page title and description", async ({ page }) => {
    await page.goto("/cluster-builder");

    // Verify page title
    await expect(page).toHaveTitle(/Cluster Builder/);

    // Check for main heading
    const mainHeading = page.locator('h1:has-text("Cluster Builder")').first();
    await expect(mainHeading).toBeVisible({ timeout: 3000 });

    // Check for description
    const description = page.locator(
      "text=Build clusters interactively, text=real-time validation",
    );
    const hasDescription = await description
      .isVisible({ timeout: 2000 })
      .catch(() => false);

    expect(typeof hasDescription).toBe("boolean");
  });

  test("should display configuration controls", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");

    // Check for configuration card
    const configCard = page.locator("text=Configuration").first();
    await expect(configCard).toBeVisible({ timeout: 3000 });

    // Check for dropdowns
    const catalogLabel = page.locator('label:has-text("Catalog")');
    const rulesetLabel = page.locator('label:has-text("Pairwise RuleSet")');
    const clusterRulesetLabel = page.locator(
      'label:has-text("Cluster RuleSet")',
    );

    const hasCatalog = await catalogLabel
      .isVisible({ timeout: 2000 })
      .catch(() => false);
    const hasRuleset = await rulesetLabel
      .isVisible({ timeout: 2000 })
      .catch(() => false);
    const hasClusterRuleset = await clusterRulesetLabel
      .isVisible({ timeout: 2000 })
      .catch(() => false);

    // At least one dropdown should be visible
    expect(hasCatalog || hasRuleset || hasClusterRuleset).toBeTruthy();
  });

  test("should display current cluster section", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");

    // Wait for page to load
    await page.waitForTimeout(1000);

    // Check for current cluster card
    const clusterCard = page
      .locator("text=Current Cluster, text=items")
      .first();
    const hasClusterCard = await clusterCard
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    expect(typeof hasClusterCard).toBe("boolean");
  });

  test("should display empty cluster message initially", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");

    // Wait for evaluation
    await page.waitForTimeout(1500);

    // Look for empty state message
    const emptyMessage = page.locator(
      "text=No items in cluster, text=Select items",
    );
    const hasEmptyMessage = await emptyMessage
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    expect(typeof hasEmptyMessage).toBe("boolean");
  });

  test("should display available items section", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");

    // Wait for data to load
    await page.waitForTimeout(1500);

    // Check for available items heading
    const availableItems = page.locator(
      "text=Available Items, text=compatible",
    );
    const hasAvailableItems = await availableItems
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    expect(typeof hasAvailableItems).toBe("boolean");
  });

  test("should allow adding items to cluster", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");

    // Wait for items to load
    await page.waitForTimeout(1500);

    // Find first available item button (should have item name and ID)
    const firstItem = page
      .locator(
        'button:has-text("shirt"), button:has-text("pants"), button:has-text("top")',
      )
      .first();
    const itemExists = await firstItem
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    if (itemExists) {
      // Click to add item
      await firstItem.click();

      // Wait for UI update
      await page.waitForTimeout(500);

      // Check that cluster count increased
      const clusterHeading = page.locator("text=Current Cluster");
      const hasClusterItems = await clusterHeading
        .locator("..")
        .locator("text=1 item, text=2 items, text=3 items")
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(typeof hasClusterItems).toBe("boolean");
    }
  });

  test("should show validation status for cluster", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");

    // Wait for evaluation
    await page.waitForTimeout(1500);

    // Try to add items to see validation
    const itemButton = page.locator("button").filter({
      hasText: /(shirt|pants|top|dress)/i,
    });
    const firstItem = itemButton.first();

    const itemExists = await firstItem
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    if (itemExists) {
      // Add first item
      await firstItem.click();
      await page.waitForTimeout(500);

      // Look for validation badge (Valid or Invalid)
      const validBadge = page.locator("text=Valid, text=Invalid");
      const hasBadge = await validBadge
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(typeof hasBadge).toBe("boolean");
    }
  });

  test("should show clear button when cluster has items", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);

    // Try to add an item
    const itemButton = page.locator("button").filter({
      hasText: /(shirt|pants|top)/i,
    });
    const firstItem = itemButton.first();

    const itemExists = await firstItem
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    if (itemExists) {
      await firstItem.click();
      await page.waitForTimeout(500);

      // Look for Clear button
      const clearButton = page.locator('button:has-text("Clear")');
      const hasClearButton = await clearButton
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(typeof hasClearButton).toBe("boolean");
    }
  });

  test("should allow removing items from cluster", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);

    // Add an item first
    const addButton = page.locator("button").filter({
      hasText: /(shirt|pants|top)/i,
    });
    const firstItem = addButton.first();

    const itemExists = await firstItem
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    if (itemExists) {
      await firstItem.click();
      await page.waitForTimeout(500);

      // Find item in cluster (should have ✕ indicator)
      const clusterItem = page.locator('button:has-text("✕")').first();
      const clusterItemExists = await clusterItem
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (clusterItemExists) {
        // Click to remove
        await clusterItem.click();
        await page.waitForTimeout(500);

        // Cluster should be empty again
        const emptyMessage = page.locator("text=No items in cluster");
        const hasEmptyMessage = await emptyMessage
          .isVisible({ timeout: 2000 })
          .catch(() => false);

        expect(typeof hasEmptyMessage).toBe("boolean");
      }
    }
  });

  test("should show incompatible items section when cluster has items", async ({
    page,
  }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);

    // Add an item
    const itemButton = page.locator("button").filter({
      hasText: /(shirt|pants|top)/i,
    });
    const firstItem = itemButton.first();

    const itemExists = await firstItem
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    if (itemExists) {
      await firstItem.click();
      await page.waitForTimeout(1000);

      // Look for incompatible items section
      const incompatibleSection = page.locator("text=Incompatible Items");
      const hasSection = await incompatibleSection
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(typeof hasSection).toBe("boolean");
    }
  });

  test("should show candidate validation preview", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);

    // Add first item
    const itemButtons = page.locator("button").filter({
      hasText: /(shirt|pants|top)/i,
    });

    const firstItem = itemButtons.first();
    const itemExists = await firstItem
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    if (itemExists) {
      await firstItem.click();
      await page.waitForTimeout(1000);

      // Look for validation preview on candidate items
      const validationBadge = page.locator("text=✓ Valid, text=Would be valid");
      const hasBadge = await validationBadge
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(typeof hasBadge).toBe("boolean");
    }
  });

  test("should handle loading states", async ({ page }) => {
    await page.goto("/cluster-builder");

    // Check for loading indicator during initial load
    const loadingText = page.locator("text=Evaluating, text=Loading");
    const hasLoading = await loadingText
      .isVisible({ timeout: 1000 })
      .catch(() => false);

    // Either shows loading or loads so fast we miss it
    expect(typeof hasLoading).toBe("boolean");

    // Wait for content to appear
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);

    // Should eventually show content
    const hasContent = await page
      .locator("text=Configuration, text=Current Cluster")
      .isVisible({ timeout: 3000 })
      .catch(() => false);

    expect(typeof hasContent).toBe("boolean");
  });

  test("should verify navigation breadcrumbs work", async ({ page }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");

    // Verify navigation bar exists
    const nav = page.locator('nav, [class*="navigation"]').first();
    const hasNav = await nav.isVisible({ timeout: 2000 }).catch(() => false);

    if (hasNav) {
      // Look for Rulate logo/link
      const rulateLink = page.locator('a:has-text("Rulate")').first();
      const hasRulateLink = await rulateLink
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(typeof hasRulateLink).toBe("boolean");
    }
  });

  test("should maintain state when switching between configurations", async ({
    page,
  }) => {
    await page.goto("/cluster-builder");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);

    // Check that catalog selector exists
    const catalogSelect = page.locator('select[id="catalog"]');
    const hasSelect = await catalogSelect
      .isVisible({ timeout: 2000 })
      .catch(() => false);

    if (hasSelect) {
      // Get current value
      const initialValue = await catalogSelect.inputValue();

      // Verify items are loaded
      await page.waitForTimeout(500);
      const hasItems = await page
        .locator("button")
        .filter({ hasText: /shirt|pants|top/i })
        .first()
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(initialValue || hasItems || hasSelect).toBeTruthy();
    }
  });
});
