import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig, type UserConfig } from "vite";
import type { TestUserConfig } from "vitest/config";

const config = {
  plugins: [sveltekit()],
  resolve: {
    alias: {
      $app: "@sveltejs/kit/src/runtime/app",
    },
  },
  optimizeDeps: {
    exclude: ["@sveltejs/kit"],
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    include: ["src/**/*.{test,spec}.{js,ts}"],
    globals: true,
    // Use happy-dom for better Svelte 5 compatibility
    environment: "happy-dom",
    setupFiles: ["./src/test-setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json-summary", "json"],
      // Only include TypeScript files - v8 can't properly instrument Svelte components
      // Svelte components are tested via unit tests but not measurable by v8
      include: ["src/**/*.ts"],
      exclude: [
        "src/**/*.test.ts",
        "src/**/*.spec.ts",
        "src/test-setup.ts",
        "src/lib/test-utils/**", // Test infrastructure, not production code
      ],
      thresholds: {
        statements: 30, // Realistic for Svelte + TS codebase
        branches: 25, // Limited by unmeasurable Svelte logic
        functions: 50,
        lines: 30,
      },
    },
  } satisfies TestUserConfig,
} satisfies UserConfig & { test: TestUserConfig };

export default defineConfig(config);
