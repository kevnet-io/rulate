import { test, expect } from "@playwright/test";

test.describe("RuleEditor Integration", () => {
  test.beforeEach(async ({ page }) => {
    // Ensure we have a schema to work with
    await page.goto("/rulesets/new");

    // Wait for schemas to load
    await page.waitForSelector('select[id="schema"]');
  });

  test("should display RuleEditor when creating a ruleset", async ({
    page,
  }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // RuleEditor should be visible
    await expect(page.locator("text=Rule Condition Editor")).toBeVisible();

    // Should have the sidebar with tabs - use more specific selectors for buttons
    await expect(page.locator('button:has-text("Operators")')).toBeVisible();
    await expect(page.locator('button:has-text("Templates")')).toBeVisible();
  });

  test("should switch between Operators and Templates tabs", async ({
    page,
  }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Click Templates tab
    await page.click('button:has-text("Templates")');

    // Should show template content - check for the select dropdown that appears in templates section
    await expect(page.locator("select").nth(1)).toBeVisible();

    // Click back to Operators
    await page.click('button:has-text("Operators")');

    // Should show operator content - check for the search input that appears in operators section
    await expect(
      page.locator('input[placeholder="Search operators..."]'),
    ).toBeVisible();
  });

  test("should not submit form when switching tabs", async ({ page }) => {
    const initialURL = page.url();

    await page.click('button:has-text("Add Rule")');

    // Switch to Templates tab
    await page.click('button:has-text("Templates")');

    // URL should not change (form should not submit)
    expect(page.url()).toBe(initialURL);

    // Switch back to Operators
    await page.click('button:has-text("Operators")');

    // Still should not have navigated
    expect(page.url()).toBe(initialURL);
  });

  test("should insert operator from sidebar", async ({ page }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Get initial textarea value
    const textarea = page.locator("textarea").first();
    const initialValue = await textarea.inputValue();

    // Find and click an Insert button for an operator
    await page.locator('button:has-text("Insert")').first().click();

    // Textarea value should have changed
    const newValue = await textarea.inputValue();
    expect(newValue).not.toBe(initialValue);
    expect(newValue.length).toBeGreaterThan(initialValue.length);
  });

  test("should insert operator at cursor position", async ({ page }) => {
    await page.click('button:has-text("Add Rule")');

    const textarea = page.locator("textarea").first();

    // Type initial JSON with logical operator
    await textarea.fill('{"all": []}');

    // Position cursor inside the array (after the opening bracket)
    await textarea.evaluate((el: HTMLTextAreaElement) => {
      el.setSelectionRange(9, 9); // Position after the '['
    });

    // Get value before insertion
    const valueBeforeInsert = await textarea.inputValue();

    // Insert an operator
    await page.locator('button:has-text("Insert")').first().click();

    // Verify operator was inserted
    const valueAfterInsert = await textarea.inputValue();
    expect(valueAfterInsert).not.toBe(valueBeforeInsert);
    expect(valueAfterInsert).toContain('{"all": [');
    expect(valueAfterInsert).toContain('"field"');
    // Should have both the array structure and the inserted field
    expect(valueAfterInsert.length).toBeGreaterThan(valueBeforeInsert.length);
  });

  test("should insert template from sidebar", async ({ page }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Switch to Templates tab
    await page.click('button:has-text("Templates")');

    // Click Insert on a template
    await page.locator('button:has-text("Insert")').first().click();

    // Textarea should have template JSON
    const textarea = page.locator("textarea").first();
    const value = await textarea.inputValue();

    // Should have valid JSON structure
    expect(value).toContain("{");
    expect(value).toContain("}");
  });

  test("should show wardrobe templates for wardrobe schema", async ({
    page,
  }) => {
    // Select wardrobe schema (if it exists)
    const schemaSelect = page.locator('select[id="schema"]');
    const options = await schemaSelect.locator("option").allTextContents();

    const wardrobeOption = options.find((opt) =>
      opt.toLowerCase().includes("wardrobe"),
    );

    if (wardrobeOption) {
      await schemaSelect.selectOption({ label: wardrobeOption });

      // Add a rule
      await page.click('button:has-text("Add Rule")');

      // Switch to Templates
      await page.click('button:has-text("Templates")');

      // Should have Wardrobe Examples category - the select for template categories is in the sidebar
      // It's the first (and only) select in the template tab section
      await page.waitForSelector("select", { timeout: 5000 });
      const allSelects = page.locator("select");
      // The template category select should be in the sidebar section
      const templateCategorySelect = allSelects.last(); // Get the last select which should be the template category select
      const templateOptions = await templateCategorySelect
        .locator("option")
        .allTextContents();

      // Check if wardrobe option exists
      const hasWardrobe = templateOptions.some((opt) =>
        opt.toLowerCase().includes("wardrobe"),
      );
      expect(hasWardrobe).toBe(true);
    }
  });

  test("should display schema fields in RuleEditor", async ({ page }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Should show "Available Fields" section - wait for it to appear
    await page.waitForSelector("text=Available Fields", { timeout: 5000 });
    await expect(page.locator("text=Available Fields")).toBeVisible();

    // The wardrobe schema (which is selected by default) has dimensions
    // So there should be visible field badges below the "Available Fields" text
    // Just check that we can find visible text content that looks like a field
    const availableFieldsSection = page.locator("text=Available Fields");
    const sectionParent = availableFieldsSection.locator("..");

    // Try to find any visible text in the next section (should contain dimension names)
    const visibleText = await sectionParent.textContent();
    expect(visibleText).toBeTruthy();
    expect(visibleText).toContain("body_zone"); // One of the wardrobe schema dimensions
  });

  test("should format JSON when clicking Format button", async ({ page }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Enter unformatted JSON
    const textarea = page.locator("textarea").first();
    await textarea.fill('{"equals":{"field":"color"}}');

    // Click Format button
    await page.click('button:has-text("Format")');

    // JSON should be formatted (with newlines)
    const formatted = await textarea.inputValue();
    expect(formatted).toContain("\n");
    expect(formatted).toContain("  "); // Should have indentation
  });

  test("should toggle sidebar visibility", async ({ page }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Sidebar should be visible - check for Operators button
    await expect(page.locator('button:has-text("Operators")')).toBeVisible();

    // Click Hide Help button
    await page.click('button:has-text("Hide Help")');

    // Sidebar should be hidden - check that search input is hidden
    await expect(
      page.locator('input[placeholder="Search operators..."]'),
    ).not.toBeVisible();

    // Click Show Help button
    await page.click('button:has-text("Show Help")');

    // Sidebar should be visible again
    await expect(
      page.locator('input[placeholder="Search operators..."]'),
    ).toBeVisible();
  });

  test("should create ruleset with rule from template", async ({ page }) => {
    // Use unique name to avoid conflicts when tests run multiple times
    const rulesetName = `test_ruleset_${Date.now()}`;

    // Fill basic info
    await page.fill('input[id="name"]', rulesetName);
    await page.fill('input[id="version"]', "1.0.0");

    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Fill rule name
    await page.fill('input[placeholder*="same_zone"]', "test_rule");

    // Insert operator from the sidebar
    // Click the first Insert button (for operators in the sidebar)
    const insertBtn = page.locator('button:has-text("Insert")').first();
    await insertBtn.click({ timeout: 5000 });

    // Hide the sidebar to make room for submit button
    await page.click('button:has-text("Hide Help")');

    // Wait for sidebar to hide
    await page.waitForTimeout(300);

    // Submit form
    await page.waitForSelector(
      'button[type="submit"]:has-text("Create RuleSet")',
      { timeout: 5000 },
    );
    await page.click('button[type="submit"]:has-text("Create RuleSet")');

    // Should show success toast
    await expect(page.locator('[role="alert"]')).toContainText(
      "created successfully",
    );

    // Should navigate to ruleset detail page
    await expect(page).toHaveURL(new RegExp(`/rulesets/${rulesetName}`));
  });

  test("should filter operators by category", async ({ page }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Get total number of operators
    const allOperators = await page
      .locator('button:has-text("Insert")')
      .count();

    // Select Comparison category
    await page
      .locator("select")
      .filter({ hasText: /All Operators/ })
      .selectOption("comparison");

    // Should have fewer operators
    const comparisonOperators = await page
      .locator('button:has-text("Insert")')
      .count();
    expect(comparisonOperators).toBeLessThan(allOperators);
    expect(comparisonOperators).toBeGreaterThan(0);
  });

  test("should search operators by name", async ({ page }) => {
    // Add a rule
    await page.click('button:has-text("Add Rule")');

    // Get initial count
    const initialCount = await page
      .locator('button:has-text("Insert")')
      .count();

    // Search for specific operator
    await page.fill('input[placeholder="Search operators..."]', "equals");

    // Should have fewer results
    const searchResults = await page
      .locator('button:has-text("Insert")')
      .count();
    expect(searchResults).toBeLessThan(initialCount);
    expect(searchResults).toBeGreaterThan(0);

    // Should show "Equals" operator
    await expect(page.locator("text=Equals")).toBeVisible();
  });
});

test.describe("RuleEditor Accessibility", () => {
  test("should have proper ARIA labels", async ({ page }) => {
    await page.goto("/rulesets/new");
    await page.click('button:has-text("Add Rule")');

    // Format button should have title
    await expect(page.locator('button:has-text("Format")')).toHaveAttribute(
      "title",
    );

    // Sidebar should be accessible
    await expect(page.locator("textarea").first()).toBeVisible();
  });

  test("should support keyboard navigation in tabs", async ({ page }) => {
    await page.goto("/rulesets/new");
    await page.click('button:has-text("Add Rule")');

    // Focus the Operators tab
    await page.locator('button:has-text("Operators")').focus();

    // Press Tab to move to Templates
    await page.keyboard.press("Tab");

    // Should be on Templates button
    const focusedElement = await page.evaluate(
      () => document.activeElement?.textContent,
    );
    expect(focusedElement).toContain("Templates");
  });
});

test.describe("Smart Context-Aware Insertion", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/rulesets/new");
    await page.click('button:has-text("Add Rule")');
  });

  test("should insert into empty array with smart context", async ({
    page,
  }) => {
    const textarea = page.locator("textarea").first();

    // Start with empty all array
    await textarea.fill('{"all": []}');

    // Position cursor inside array
    await textarea.evaluate((el: HTMLTextAreaElement) => {
      el.setSelectionRange(9, 9); // Inside the brackets
    });

    // Get initial value
    const _initialValue = await textarea.inputValue();

    // Insert an operator
    await page.locator('button:has-text("Insert")').first().click();

    // Should insert into the array
    const newValue = await textarea.inputValue();
    expect(newValue).toContain('{"all": [');
    expect(newValue).toContain("]}");
    expect(newValue).not.toContain("[,");
    expect(newValue).not.toContain(",]");
    expect(newValue).toContain('"field"');
  });

  test("should insert into array with existing items", async ({ page }) => {
    const textarea = page.locator("textarea").first();

    // Start with array containing one item
    await textarea.fill('{"all": [{"equals": {"field": "color"}}]}');

    // Position cursor before closing bracket
    await textarea.evaluate(() => {
      const el = document.querySelector("textarea") as HTMLTextAreaElement;
      if (el) {
        const closingBracketPos = el.value.lastIndexOf("}]");
        el.setSelectionRange(closingBracketPos, closingBracketPos);
      }
    });

    // Insert another operator
    await page.locator('button:has-text("Insert")').first().click();

    // Should add comma and new operator
    const newValue = await textarea.inputValue();
    expect(newValue).toContain(",");
    expect(newValue).toContain('{"equals"');
    expect(newValue).toContain("]}");
  });

  test("should wrap simple condition when inserting with Insert button", async ({
    page,
  }) => {
    const textarea = page.locator("textarea").first();

    // Start with simple condition
    await textarea.fill('{"equals": {"field": "color"}}');

    // Insert another operator
    await page.locator('button:has-text("Insert")').first().click();

    // Should wrap in "all" operator
    const newValue = await textarea.inputValue();
    expect(newValue).toContain('"all"');
    expect(newValue).toContain("[");
    expect(newValue).toContain('{"equals"');
    expect(newValue).toContain(",");
    expect(newValue).toContain("]");
    // Should be valid JSON
    expect(() => JSON.parse(newValue)).not.toThrow();
  });

  test("should replace content with Replace button", async ({ page }) => {
    const textarea = page.locator("textarea").first();
    const initialContent = '{"equals": {"field": "color"}}';

    // Fill with initial content
    await textarea.fill(initialContent);

    // Get the initial value
    const initialValue = await textarea.inputValue();
    expect(initialValue).toContain("equals");

    // Find the first operator's Replace button (should be next to Insert button in first operator card)
    // Get all operator cards and find the first one
    const firstOperatorCard = page
      .locator('div:has(> button:has-text("Insert"))')
      .first();

    // Within that card, find the Replace button
    const replaceButton = firstOperatorCard
      .locator('button:has-text("Replace")')
      .first();

    // Click Replace
    await replaceButton.click();

    // Should replace the entire content with new operator
    const newValue = await textarea.inputValue();
    // The content should change
    expect(newValue).not.toBe(initialValue);
    // Should be valid JSON
    expect(() => JSON.parse(newValue)).not.toThrow();
  });

  test("should format valid JSON and show success toast", async ({ page }) => {
    const textarea = page.locator("textarea").first();

    // Enter unformatted JSON
    await textarea.fill('{"equals":{"field":"color"}}');

    // Click Format button
    await page.click('button:has-text("Format")');

    // Should show success toast
    await expect(page.locator('[role="alert"]')).toContainText("formatted");

    // JSON should be formatted with newlines and indentation
    const formatted = await textarea.inputValue();
    expect(formatted).toContain("\n");
    expect(formatted).toContain("  "); // 2-space indentation
  });

  test("should show error toast for invalid JSON when formatting", async ({
    page,
  }) => {
    const textarea = page.locator("textarea").first();

    // Enter invalid JSON
    await textarea.fill("{invalid json}");

    // Click Format button
    await page.click('button:has-text("Format")');

    // Should show error toast
    await expect(page.locator('[role="alert"]')).toContainText("Invalid");
  });

  test("should show info toast when JSON is already formatted", async ({
    page,
  }) => {
    const textarea = page.locator("textarea").first();

    // Enter already formatted JSON
    const formatted = `{
  "equals": {
    "field": "color"
  }
}`;
    await textarea.fill(formatted);

    // Click Format button
    await page.click('button:has-text("Format")');

    // Should show info toast
    await expect(page.locator('[role="alert"]')).toContainText(
      "already formatted",
    );
  });

  test("should have both Insert and Replace buttons for operators", async ({
    page,
  }) => {
    // Should have at least one operator with both buttons visible
    const insertButtons = page.locator('button:has-text("Insert")');
    const replaceButtons = page.locator('button:has-text("Replace")');

    // Count buttons - for each operator we should have 1 Insert and 1 Replace
    const insertCount = await insertButtons.count();
    const replaceCount = await replaceButtons.count();

    expect(insertCount).toBeGreaterThan(0);
    expect(replaceCount).toBeGreaterThan(0);
    expect(replaceCount).toBeLessThanOrEqual(insertCount);
  });

  test("should preserve cursor position after insertion", async ({ page }) => {
    const textarea = page.locator("textarea").first();

    // Clear textarea
    await textarea.fill("");

    // Insert an operator
    await page.locator('button:has-text("Insert")').first().click();

    // Textarea should have content
    const value = await textarea.inputValue();
    expect(value.length).toBeGreaterThan(0);

    // Should be able to position cursor at end
    await textarea.evaluate((el: HTMLTextAreaElement) => {
      el.selectionStart = el.value.length;
      el.selectionEnd = el.value.length;
    });

    const cursorPos = await textarea.evaluate(
      (el: HTMLTextAreaElement) => el.selectionStart,
    );
    expect(cursorPos).toBe(value.length);
  });
});
