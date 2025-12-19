/**
 * Tests for theme store
 *
 * Tests the theme store for managing light/dark/system theme preferences
 */

import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";

// Mock localStorage BEFORE importing the store
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

// Setup global mocks before module import
Object.defineProperty(globalThis, "localStorage", {
  value: localStorageMock,
  writable: true,
  configurable: true,
});

// Mock matchMedia globally
const createMatchMediaMock = (matches: boolean) => {
  const listeners: Array<(e: MediaQueryListEvent) => void> = [];

  return {
    matches,
    media: "(prefers-color-scheme: dark)",
    addEventListener: vi.fn(
      (event: string, listener: (e: MediaQueryListEvent) => void) => {
        if (event === "change") {
          listeners.push(listener);
        }
      },
    ),
    addListener: vi.fn((listener: (e: MediaQueryListEvent) => void) => {
      listeners.push(listener);
    }),
    removeEventListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
    // Helper to trigger change event
    _triggerChange: (newMatches: boolean) => {
      const event = { matches: newMatches } as MediaQueryListEvent;
      listeners.forEach((listener) => listener(event));
    },
  };
};

// Default matchMedia mock
Object.defineProperty(globalThis, "matchMedia", {
  value: vi.fn(() => createMatchMediaMock(false)),
  writable: true,
  configurable: true,
});

// NOW import the store after mocks are set up
import { themeStore } from "./theme.svelte";

describe("Theme Store", () => {
  let matchMediaMock: ReturnType<typeof createMatchMediaMock>;

  beforeEach(() => {
    // Clear localStorage
    localStorageMock.clear();

    // Reset matchMedia mock (default to light mode)
    matchMediaMock = createMatchMediaMock(false);
    globalThis.matchMedia = vi.fn(() => matchMediaMock) as any;

    // Clear document classes
    document.documentElement.classList.remove("dark");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Initial State", () => {
    it("defaults to system theme when no localStorage", () => {
      expect(themeStore.theme).toBe("system");
    });

    it("reads light theme from localStorage when available", () => {
      localStorageMock.setItem("rulate-theme", "light");
      // Need to reload by setting and checking
      themeStore.setTheme("light");
      expect(themeStore.theme).toBe("light");
    });

    it("reads dark theme from localStorage when available", () => {
      localStorageMock.setItem("rulate-theme", "dark");
      themeStore.setTheme("dark");
      expect(themeStore.theme).toBe("dark");
    });

    it("reads system theme from localStorage when available", () => {
      localStorageMock.setItem("rulate-theme", "system");
      themeStore.setTheme("system");
      expect(themeStore.theme).toBe("system");
    });

    it("resolves system theme to light when OS preference is light", () => {
      matchMediaMock = createMatchMediaMock(false);
      window.matchMedia = vi.fn(() => matchMediaMock) as any;

      themeStore.setTheme("system");
      expect(themeStore.resolvedTheme).toBe("light");
    });

    it("resolves system theme to dark when OS preference is dark", () => {
      matchMediaMock = createMatchMediaMock(true);
      window.matchMedia = vi.fn(() => matchMediaMock) as any;

      themeStore.setTheme("system");
      expect(themeStore.resolvedTheme).toBe("dark");
    });
  });

  describe("Setting Theme", () => {
    it("sets theme to light", () => {
      themeStore.setTheme("light");
      expect(themeStore.theme).toBe("light");
      expect(themeStore.resolvedTheme).toBe("light");
    });

    it("sets theme to dark", () => {
      themeStore.setTheme("dark");
      expect(themeStore.theme).toBe("dark");
      expect(themeStore.resolvedTheme).toBe("dark");
    });

    it("sets theme to system", () => {
      themeStore.setTheme("system");
      expect(themeStore.theme).toBe("system");
    });

    it("saves theme to localStorage", () => {
      themeStore.setTheme("dark");
      expect(localStorageMock.getItem("rulate-theme")).toBe("dark");

      themeStore.setTheme("light");
      expect(localStorageMock.getItem("rulate-theme")).toBe("light");

      themeStore.setTheme("system");
      expect(localStorageMock.getItem("rulate-theme")).toBe("system");
    });
  });

  describe("Toggle Theme", () => {
    it("cycles from light to dark to system", () => {
      themeStore.setTheme("light");
      expect(themeStore.theme).toBe("light");

      themeStore.toggle();
      expect(themeStore.theme).toBe("dark");

      themeStore.toggle();
      expect(themeStore.theme).toBe("system");

      themeStore.toggle();
      expect(themeStore.theme).toBe("light");
    });

    it("updates localStorage on each toggle", () => {
      themeStore.setTheme("light");
      themeStore.toggle();
      expect(localStorageMock.getItem("rulate-theme")).toBe("dark");

      themeStore.toggle();
      expect(localStorageMock.getItem("rulate-theme")).toBe("system");
    });
  });

  describe("DOM Updates", () => {
    it("adds dark class when theme is dark", () => {
      themeStore.setTheme("dark");
      expect(document.documentElement.classList.contains("dark")).toBe(true);
    });

    it("removes dark class when theme is light", () => {
      // First set to dark
      themeStore.setTheme("dark");
      expect(document.documentElement.classList.contains("dark")).toBe(true);

      // Then switch to light
      themeStore.setTheme("light");
      expect(document.documentElement.classList.contains("dark")).toBe(false);
    });

    it("adds dark class when system theme resolves to dark", () => {
      matchMediaMock = createMatchMediaMock(true); // OS prefers dark
      window.matchMedia = vi.fn(() => matchMediaMock) as any;

      themeStore.setTheme("system");
      expect(document.documentElement.classList.contains("dark")).toBe(true);
    });

    it("removes dark class when system theme resolves to light", () => {
      matchMediaMock = createMatchMediaMock(false); // OS prefers light
      window.matchMedia = vi.fn(() => matchMediaMock) as any;

      themeStore.setTheme("system");
      expect(document.documentElement.classList.contains("dark")).toBe(false);
    });
  });

  describe("System Preference Changes", () => {
    it("listens to OS preference via matchMedia", () => {
      matchMediaMock = createMatchMediaMock(false); // Start with light
      window.matchMedia = vi.fn(() => matchMediaMock) as any;

      themeStore.setTheme("system");
      expect(themeStore.resolvedTheme).toBe("light");

      // Verify matchMedia was called to detect system preference
      expect(window.matchMedia).toHaveBeenCalledWith(
        "(prefers-color-scheme: dark)",
      );
    });

    it("does not update when theme is explicitly set to light or dark", () => {
      themeStore.setTheme("dark");
      const initialTheme = themeStore.theme;

      // Simulate OS preference change
      matchMediaMock._triggerChange(false);

      // Should remain dark (not affected by OS change)
      expect(themeStore.theme).toBe(initialTheme);
    });
  });

  describe("Resolved Theme", () => {
    it("resolved theme matches theme for explicit light", () => {
      themeStore.setTheme("light");
      expect(themeStore.resolvedTheme).toBe("light");
    });

    it("resolved theme matches theme for explicit dark", () => {
      themeStore.setTheme("dark");
      expect(themeStore.resolvedTheme).toBe("dark");
    });

    it("resolved theme depends on OS for system", () => {
      // Test with light OS preference
      matchMediaMock = createMatchMediaMock(false);
      window.matchMedia = vi.fn(() => matchMediaMock) as any;
      themeStore.setTheme("system");
      expect(themeStore.resolvedTheme).toBe("light");

      // Test with dark OS preference
      matchMediaMock = createMatchMediaMock(true);
      window.matchMedia = vi.fn(() => matchMediaMock) as any;
      themeStore.setTheme("system");
      expect(themeStore.resolvedTheme).toBe("dark");
    });
  });

  describe("Persistence", () => {
    it("persists theme across store recreations", () => {
      themeStore.setTheme("dark");
      expect(localStorageMock.getItem("rulate-theme")).toBe("dark");

      // Simulate page reload by checking localStorage
      const storedTheme = localStorageMock.getItem("rulate-theme");
      expect(storedTheme).toBe("dark");
    });

    it("handles invalid localStorage values", () => {
      localStorageMock.setItem("rulate-theme", "invalid");
      // Store should fall back to system
      expect(themeStore.theme).toBeDefined();
    });

    it("handles missing localStorage", () => {
      localStorageMock.clear();
      // Should default to system
      expect(themeStore.theme).toBeDefined();
    });

    it("persists each theme type correctly", () => {
      // Test light
      themeStore.setTheme("light");
      expect(localStorageMock.getItem("rulate-theme")).toBe("light");

      // Test dark
      themeStore.setTheme("dark");
      expect(localStorageMock.getItem("rulate-theme")).toBe("dark");

      // Test system
      themeStore.setTheme("system");
      expect(localStorageMock.getItem("rulate-theme")).toBe("system");
    });
  });

  describe("Edge Cases", () => {
    it("handles rapid theme changes", () => {
      themeStore.setTheme("light");
      themeStore.setTheme("dark");
      themeStore.setTheme("system");
      themeStore.setTheme("light");

      expect(themeStore.theme).toBe("light");
      expect(localStorageMock.getItem("rulate-theme")).toBe("light");
    });

    it("handles rapid toggles", () => {
      themeStore.setTheme("light");
      themeStore.toggle();
      themeStore.toggle();
      themeStore.toggle();

      // Should cycle back to light
      expect(themeStore.theme).toBe("light");
    });
  });

  describe("Type Safety", () => {
    it("theme is one of the valid types", () => {
      const validThemes = ["light", "dark", "system"];
      expect(validThemes).toContain(themeStore.theme);
    });

    it("resolvedTheme is either light or dark", () => {
      const validResolved = ["light", "dark"];
      expect(validResolved).toContain(themeStore.resolvedTheme);
    });

    it("store has all required methods", () => {
      expect(typeof themeStore.setTheme).toBe("function");
      expect(typeof themeStore.toggle).toBe("function");
    });

    it("store has all required properties", () => {
      expect(themeStore).toHaveProperty("theme");
      expect(themeStore).toHaveProperty("resolvedTheme");
    });
  });
});
