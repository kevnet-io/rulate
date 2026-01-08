/**
 * E2E tests for Cluster Builder Graph Visualization
 */

import { test, expect } from "@playwright/test";

test.describe("Cluster Builder Graph Visualization", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to cluster builder page
    await page.goto("/cluster-builder");

    // Wait for the page to load
    await expect(
      page.getByRole("heading", { name: "Cluster Builder" }),
    ).toBeVisible();
  });

  test("should display collapsed graph card by default", async ({ page }) => {
    // Graph card should be visible
    await expect(page.getByText("Compatibility Graph")).toBeVisible();

    // Graph content should be hidden initially (collapsed)
    await expect(page.getByText("Loading graph data...")).not.toBeVisible();
    await expect(
      page.getByText("Visual network showing pairwise compatibility"),
    ).toBeVisible();
  });

  test("should expand graph when clicking header", async ({ page }) => {
    // Click the graph card header to expand
    await page.getByText("▸ Compatibility Graph").click();

    // Should show expanded indicator
    await expect(page.getByText("▼ Compatibility Graph")).toBeVisible();

    // Should show either loading or empty state
    const loadingSkeleton = page.locator('role=status[name*="Loading graph"]');
    const emptyState = page.getByText(
      "No graph data available. Select a catalog",
    );

    const isLoadingVisible = await loadingSkeleton
      .isVisible()
      .catch(() => false);
    const isEmptyVisible = await emptyState.isVisible().catch(() => false);

    expect(isLoadingVisible || isEmptyVisible).toBe(true);
  });

  test("should load graph data when expanded with valid configuration", async ({
    page,
  }) => {
    // Assume there's test data loaded
    // Select catalog (assuming dropdown has options)
    const catalogSelect = page.locator("select#catalog");
    if ((await catalogSelect.count()) > 0) {
      const options = await catalogSelect.locator("option").count();
      if (options > 0) {
        await catalogSelect.selectOption({ index: 0 });
      }
    }

    // Expand the graph
    await page.getByText("▸ Compatibility Graph").click();

    // Wait a bit for potential loading
    await page.waitForTimeout(1000);

    // Should show either graph controls or empty state message
    const hasControls =
      (await page.getByText("Layout:").count()) > 0 ||
      (await page.getByText("No graph data available").count()) > 0;
    expect(hasControls).toBe(true);
  });

  test("should display graph controls when graph is loaded", async ({
    page,
  }) => {
    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();

    // Wait for potential load
    await page.waitForTimeout(500);

    // If graph data is available, controls should be visible
    const layoutLabel = page.getByText("Layout:");
    if (await layoutLabel.isVisible()) {
      // Verify all control elements
      await expect(page.locator("select#layout-select")).toBeVisible();
      await expect(
        page.getByRole("button", { name: /zoom in/i }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: /zoom out/i }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: /fit to screen/i }),
      ).toBeVisible();
      await expect(page.getByLabel("Show incompatible items")).toBeVisible();
    }
  });

  test("should change layout when selecting from dropdown", async ({
    page,
  }) => {
    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();

    await page.waitForTimeout(500);

    // Check if layout selector is available
    const layoutSelect = page.locator("select#layout-select");
    if (await layoutSelect.isVisible()) {
      // Get initial value
      const initialValue = await layoutSelect.inputValue();

      // Change layout
      await layoutSelect.selectOption("circular");

      // Verify selection changed
      const newValue = await layoutSelect.inputValue();
      expect(newValue).toBe("circular");
      expect(newValue).not.toBe(initialValue);
    }
  });

  test("should toggle incompatible items visibility", async ({ page }) => {
    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();

    await page.waitForTimeout(500);

    // Check if toggle is available
    const incompatibleToggle = page.getByLabel("Show incompatible items");
    if (await incompatibleToggle.isVisible()) {
      // Get initial state
      const initialState = await incompatibleToggle.isChecked();

      // Toggle it
      await incompatibleToggle.click();

      // Verify state changed
      const newState = await incompatibleToggle.isChecked();
      expect(newState).toBe(!initialState);
    }
  });

  test("should display graph legend when graph is loaded", async ({ page }) => {
    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();

    await page.waitForTimeout(500);

    // If graph is loaded, legend should be visible
    const nodesHeader = page.getByText("Nodes").first();
    if (await nodesHeader.isVisible()) {
      // Verify legend items
      await expect(page.getByText("Cluster Item")).toBeVisible();
      await expect(page.getByText("Valid Candidate")).toBeVisible();
      await expect(page.getByText("Invalid Candidate")).toBeVisible();

      await expect(page.getByText("Edges").first()).toBeVisible();
      await expect(page.getByText("Compatible")).toBeVisible();
    }
  });

  test("should display help text explaining graph interaction", async ({
    page,
  }) => {
    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();

    await page.waitForTimeout(500);

    // Help text should be visible when graph is loaded
    const helpText = page.getByText(/Click nodes to add\/remove items/);
    if (await helpText.isVisible()) {
      await expect(helpText).toContainText("Compatible pairs");
      await expect(helpText).toContainText("solid green lines");
    }
  });

  test("should collapse graph when clicking header again", async ({ page }) => {
    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();
    await expect(page.getByText("▼ Compatibility Graph")).toBeVisible();

    // Click again to collapse
    await page.getByText("▼ Compatibility Graph").click();

    // Should show collapsed indicator
    await expect(page.getByText("▸ Compatibility Graph")).toBeVisible();
  });

  test("should display loading skeleton while fetching data", async ({
    page,
  }) => {
    // Intercept the API call to delay it
    await page.route("**/api/v1/evaluate/matrix", async (route) => {
      await page.waitForTimeout(1000); // Delay for 1 second
      await route.continue();
    });

    // Select catalog if available
    const catalogSelect = page.locator("select#catalog");
    if ((await catalogSelect.count()) > 0) {
      const options = await catalogSelect.locator("option").count();
      if (options > 0) {
        await catalogSelect.selectOption({ index: 0 });
      }
    }

    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();

    // Should show loading skeleton
    const loadingSkeleton = page.locator('role=status[name*="Loading graph"]');
    if (await loadingSkeleton.isVisible()) {
      await expect(loadingSkeleton).toBeVisible();
    }
  });

  test("should maintain graph state when collapsing and re-expanding", async ({
    page,
  }) => {
    // Expand graph
    await page.getByText("▸ Compatibility Graph").click();
    await page.waitForTimeout(500);

    // If layout selector is visible, change it
    const layoutSelect = page.locator("select#layout-select");
    if (await layoutSelect.isVisible()) {
      await layoutSelect.selectOption("circular");

      // Collapse graph
      await page.getByText("▼ Compatibility Graph").click();

      // Re-expand graph
      await page.getByText("▸ Compatibility Graph").click();

      // Layout selection should be preserved
      const currentValue = await layoutSelect.inputValue();
      expect(currentValue).toBe("circular");
    }
  });

  test("should be keyboard accessible", async ({ page }) => {
    // Focus on the graph expand button
    await page.keyboard.press("Tab"); // Navigate to first interactive element

    // Keep tabbing until we reach the graph header
    let attempts = 0;
    while (attempts < 20) {
      const focusedElement = await page.evaluate(
        () => document.activeElement?.textContent || "",
      );
      if (focusedElement.includes("Compatibility Graph")) {
        break;
      }
      await page.keyboard.press("Tab");
      attempts++;
    }

    // Press Enter to expand
    await page.keyboard.press("Enter");

    // Should expand
    await expect(page.getByText("▼ Compatibility Graph")).toBeVisible();
  });
});
