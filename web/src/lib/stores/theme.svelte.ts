/**
 * Theme store
 * Manages light/dark/system theme preference with localStorage persistence
 */

export type Theme = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

export interface ThemeStore {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
  toggle: () => void;
}

const STORAGE_KEY = "rulate-theme";
const THEMES: Theme[] = ["light", "dark", "system"];

/**
 * Get the resolved theme (light or dark) based on user preference and system settings
 */
function getResolvedTheme(theme: Theme): ResolvedTheme {
  if (theme === "system") {
    // Only access window in browser context
    if (typeof window !== "undefined") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    return "light"; // SSR fallback
  }
  return theme;
}

/**
 * Apply theme class to document
 */
function applyTheme(resolved: ResolvedTheme): void {
  if (typeof document !== "undefined") {
    if (resolved === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }
}

/**
 * Load theme from localStorage
 */
function loadTheme(): Theme {
  if (typeof window === "undefined") {
    return "system";
  }

  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }

  return "system";
}

/**
 * Save theme to localStorage
 */
function saveTheme(theme: Theme): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, theme);
  }
}

function createThemeStore(): ThemeStore {
  let theme = $state<Theme>(loadTheme());
  let resolvedTheme = $state<ResolvedTheme>(getResolvedTheme(theme));

  // Apply initial theme
  applyTheme(resolvedTheme);

  // Listen for system theme changes (browser only)
  if (typeof window !== "undefined") {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleChange = () => {
      if (theme === "system") {
        const newResolved = getResolvedTheme("system");
        resolvedTheme = newResolved;
        applyTheme(newResolved);
      }
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleChange);
    } else {
      // Legacy Safari
      mediaQuery.addListener(handleChange);
    }
  }

  function setTheme(newTheme: Theme) {
    theme = newTheme;
    resolvedTheme = getResolvedTheme(newTheme);
    saveTheme(newTheme);
    applyTheme(resolvedTheme);
  }

  function toggle() {
    const currentIndex = THEMES.indexOf(theme);
    const nextIndex = (currentIndex + 1) % THEMES.length;
    setTheme(THEMES[nextIndex]);
  }

  return {
    get theme() {
      return theme;
    },
    get resolvedTheme() {
      return resolvedTheme;
    },
    setTheme,
    toggle,
  };
}

export const themeStore = createThemeStore();
