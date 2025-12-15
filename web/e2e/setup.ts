import { execSync, spawn } from "child_process";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import fs from "fs";

let apiProcess: ReturnType<typeof spawn> | null = null;

/**
 * Global setup for e2e tests
 * This runs before all e2e tests and ensures the database is seeded with test data
 */
export default async function globalSetup() {
  console.log("\n🔧 Setting up e2e test environment...\n");

  // Get the directory where this file is located (/path/to/rulate/web/e2e)
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);

  // Project root is 2 levels up from e2e/setup.ts: rulate/web/e2e -> rulate
  const projectRoot = resolve(__dirname, "..", "..");

  // Build frontend for production
  console.log("📦 Building frontend for E2E tests...");
  try {
    execSync("npm run build", {
      cwd: resolve(projectRoot, "web"),
      stdio: "inherit",
    });
    console.log("✓ Frontend built successfully\n");
  } catch {
    console.error("\n❌ Failed to build frontend\n");
    process.exit(1);
  }

  // Clear e2e database for fresh state
  console.log("🗑️  Clearing e2e database...");
  const e2eDbPath = resolve(projectRoot, "e2e_test.db");
  if (fs.existsSync(e2eDbPath)) {
    try {
      fs.unlinkSync(e2eDbPath);
      console.log("✓ E2E database cleared\n");
    } catch (_error) {
      console.error(
        `⚠️  Warning: Could not delete existing e2e database: ${_error}\n`,
      );
    }
  }

  // Start unified production server (serves API + built frontend)
  console.log("🚀 Starting unified production server with e2e database...");
  try {
    apiProcess = spawn(
      "uv",
      ["run", "python3", "-m", "uvicorn", "api.main:app", "--port", "8000"],
      {
        cwd: projectRoot,
        env: {
          ...process.env,
          DATABASE_URL: "sqlite:///./e2e_test.db",
        },
        stdio: "pipe",
      },
    );

    // Suppress API logs but capture errors
    apiProcess.stdout?.on("data", () => {
      // Suppress normal output
    });
    apiProcess.stderr?.on("data", (data) => {
      // Only show actual errors
      const msg = data.toString();
      if (!msg.includes("Uvicorn running") && msg.includes("error")) {
        console.error(msg);
      }
    });

    // Store process ID for cleanup
    const apiPid = apiProcess.pid;
    console.log(`✓ API server started (PID: ${apiPid})\n`);
  } catch {
    console.error(
      "\n❌ Failed to start API server. Make sure:\n" +
        "   1. uv is installed: uv --version\n" +
        "   2. Dependencies are installed: uv sync --dev\n",
    );
    process.exit(1);
  }

  // Wait for API server to be ready
  const apiUrl = "http://localhost:8000/api/v1";
  let isApiReady = false;
  const maxAttempts = 30;
  let attempt = 0;

  console.log("⏳ Waiting for API server to be ready...");
  while (!isApiReady && attempt < maxAttempts) {
    try {
      const response = await fetch(`${apiUrl}/schemas`);
      if (response.ok) {
        isApiReady = true;
        console.log("✓ API server is ready\n");
      }
    } catch {
      // API not ready yet
    }
    attempt++;
    if (!isApiReady) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }

  if (!isApiReady) {
    console.error("\n❌ API server did not become ready within 30 seconds\n");
    if (apiProcess) {
      apiProcess.kill();
    }
    process.exit(1);
  }

  // Seed database with test data
  console.log("🌱 Seeding database with test data...");
  try {
    const scriptPath = resolve(projectRoot, "scripts", "seed_database.py");

    // Use uv to run the script with the proper Python environment
    execSync(`uv run python3 "${scriptPath}" --api-url "${apiUrl}"`, {
      stdio: "inherit",
      cwd: projectRoot,
    });
    console.log("\n✓ Database seeded successfully\n");
  } catch {
    console.error("\n❌ Failed to seed database\n");
    if (apiProcess) {
      apiProcess.kill();
    }
    process.exit(1);
  }

  // Return cleanup function for after tests complete
  return async () => {
    if (apiProcess) {
      console.log("\n🛑 Stopping API server...");
      apiProcess.kill("SIGTERM");
      // Wait a bit for graceful shutdown
      await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log("✓ API server stopped\n");
    }
  };
}
