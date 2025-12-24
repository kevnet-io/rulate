# E2E Testing Guide

This document explains how to run end-to-end tests for the Rulate web frontend.

## Prerequisites

Before running e2e tests, you need:

1. **uv** installed (Python package manager)
2. **Python 3.14** (for backend and database seeding)
3. **Node.js 22 LTS** (for frontend)
4. **Frontend dependencies** installed via `npm install`
5. **Backend dependencies** installed via `uv sync --dev`

**Note**: Playwright browsers will be installed automatically when running tests via `make test-e2e` or `npm run test:e2e`. The test script includes `npx playwright install --with-deps` to ensure all required browsers and system dependencies are present.

## Setup

The E2E tests run against a production build of the application:

```bash
npm run test:e2e
```

Playwright will automatically:

1. Build the frontend (`npm run build`)
2. Start the unified production server on port 8000
3. Run tests against http://localhost:8000
4. Shut down the server after tests complete

The global setup script:

- ✓ Builds the frontend for production
- ✓ Clears the e2e database (`e2e_test.db`) for a fresh state
- ✓ Starts the unified production server (API + frontend) with the e2e database
- ✓ Waits for the server to be ready
- ✓ Seeds the database with test data (wardrobe v2 domain from v2.json: 53 items)

**Manual server** (optional):

```bash
# From project root
make serve-production
npm run test:e2e  # Reuses existing server
```

### Run E2E Tests

**Run all tests:**

```bash
npm run test:e2e
```

**Run tests in specific browsers:**

```bash
# Chromium only (fastest)
npm run test:e2e -- --project=chromium

# Firefox only
npm run test:e2e -- --project=firefox

# WebKit (Safari) only
npm run test:e2e -- --project=webkit
```

**Run specific test file:**

```bash
npm run test:e2e -- rule-editor.spec.ts
```

**Run specific test:**

```bash
npm run test:e2e -- rule-editor.spec.ts:12
```

**Note**: Each test run clears and recreates the e2e database, so tests start with a clean, known state.

### 3. Debug Mode

To debug tests with Playwright Inspector:

```bash
npm run test:e2e:debug
```

This opens an interactive debugger where you can step through tests.

### 4. View HTML Report

After tests complete, view the HTML report:

```bash
npx playwright show-report
```

## How It Works

### Global Setup (`e2e/setup.ts`)

The `globalSetup` file runs before all tests and:

1. **Waits for API** - Polls `http://localhost:8000/api/v1/schemas` until the API responds
2. **Seeds Database** - Runs `scripts/seed_database.py` which:
   - Loads the v2 wardrobe domain from `examples/wardrobe/v2.json`
   - Imports complete domain via `/api/v1/import/all` (53 items, gender-agnostic coverage-layer modeling)
3. **Reports Status** - Shows setup progress in the console

### WebServer Configuration

Playwright automatically starts the frontend dev server (`npm run dev`) on port 5173 with the `vite` build.

### Database State

- **E2E Database Isolation**: Tests use a separate `e2e_test.db` file to avoid affecting your development database
- **Fresh State Per Run**: The e2e database is automatically deleted and recreated before each test run
- **Seeded Data**: Database is seeded with wardrobe example data before tests run
- **Test Isolation**: Tests use the seeded data but do NOT modify the database
- **CI vs Local**:
  - **CI**: Always starts a fresh frontend server and uses a temporary e2e database
  - **Local**: Reuses the frontend server if already running (faster iteration), but always clears e2e database

## Troubleshooting

### Tests timeout waiting for API

**Problem**: Tests timeout or API server fails to start

**Solution**:

1. Ensure all dependencies are installed:
   ```bash
   uv sync --dev
   npm install
   ```
2. Check if port 8000 is already in use:
   ```bash
   lsof -i :8000
   ```
   If in use, kill the process:
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```
3. Run tests again:
   ```bash
   npm run test:e2e
   ```

### Database seeding fails

**Problem**: Setup fails at the "Seeding database" step

**Solution**:

1. Ensure all Python dependencies are installed:
   ```bash
   uv sync --dev
   ```
2. Verify example data files exist:
   ```bash
   ls examples/wardrobe/
   ```
3. Check that the example files are valid JSON:
   ```bash
   uv run python3 -c "import json; json.load(open('examples/wardrobe/v2.json'))"
   ```

### Stale frontend server causing test failures

**Problem**: Tests pass sometimes but fail other times

**Solution**: In CI, set `CI=true` environment variable to force fresh server:

```bash
CI=true npm run test:e2e
```

Locally, you can manually kill stale processes:

```bash
lsof -ti:5173 | xargs kill -9
npm run test:e2e
```

### Port already in use

**Problem**: `Error: Port 5173 is in use`

**Solution**: Kill any process using that port:

```bash
# macOS/Linux
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

## Test Structure

Tests are organized by feature:

- **`rule-editor.spec.ts`** - RuleEditor component and rule creation
- **`ux-components.spec.ts`** - Toast notifications and modal dialogs
- **`catalog-management.spec.ts`** - Creating and managing catalogs
- **`schema-management.spec.ts`** - Creating and managing schemas
- **`explorer.spec.ts`** - Interactive compatibility explorer
- **`navigation.spec.ts`** - Navigation and routing

## Best Practices

1. **Always start with the backend** - API server must be running first
2. **Use the debug mode** - When tests fail, use `npm run test:e2e:debug` to investigate
3. **Check the HTML report** - View `playwright-report/` for screenshots and traces
4. **Test in CI mode locally** - Set `CI=true` to ensure consistency
5. **Increase timeout for slow machines** - Edit `timeout` in `playwright.config.ts` if needed

## Adding New Tests

When adding new e2e tests:

1. **Use the existing selectors** - Check other tests for selector patterns
2. **Wait for content** - Use `waitForSelector()` or `expect()` for content
3. **Clean up test data** - Tests should not depend on specific order
4. **Use meaningful names** - Test names should describe what they test
5. **Reference existing fixtures** - See `fixtures.ts` for mock data patterns

Example:

```typescript
test("should create a schema", async ({ page }) => {
  await page.goto("/schemas/new");

  await page.fill('input[name="name"]', "my_schema");
  await page.click('button:has-text("Create Schema")');

  await expect(page.locator('h1:has-text("my_schema")')).toBeVisible();
});
```

## CI Integration

GitHub Actions runs E2E tests in `.github/workflows/test.yml`:

1. Builds the frontend
2. Starts the production server on port 8000
3. Runs Playwright tests across 3 browsers
4. Uploads test reports as artifacts

The CI setup matches local development - same unified server, same test configuration.

For CI pipelines, set the `CI` environment variable:

```bash
CI=true npm run test:e2e
```

This ensures:

- Fresh production build each run
- No server reuse
- Consistent test environment
- Proper error reporting
