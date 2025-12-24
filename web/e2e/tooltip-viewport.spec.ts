import { test, expect, type Locator, type Page } from "@playwright/test";

async function expectInViewport(locator: Locator, page: Page, padding = 2) {
  const box = await locator.boundingBox();
  expect(box, "Tooltip should have a bounding box").not.toBeNull();

  const viewport = await page.evaluate(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
  }));

  const xEnd = (box?.x ?? 0) + (box?.width ?? 0);
  const yEnd = (box?.y ?? 0) + (box?.height ?? 0);

  expect(box?.x ?? 0).toBeGreaterThanOrEqual(padding);
  expect(box?.y ?? 0).toBeGreaterThanOrEqual(padding);
  expect(xEnd).toBeLessThanOrEqual(viewport.width - padding);
  expect(yEnd).toBeLessThanOrEqual(viewport.height - padding);
}

test.describe("Tooltip viewport safety", () => {
  test("theme toggle tooltip stays within the viewport", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const toggle = page.locator('button[aria-label="Toggle theme"]');

    await toggle.hover();
    const tooltip = page.locator('[role="tooltip"]').first();
    await expect(tooltip).toBeVisible();
    await expectInViewport(tooltip, page);

    // Cycle to dark mode and verify again.
    await toggle.click();
    await toggle.hover();
    await expect(tooltip).toBeVisible();
    await expectInViewport(tooltip, page);
  });
});
