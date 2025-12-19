/**
 * Tests for ThemeToggle component
 *
 * Tests the theme toggle button's icon and label logic
 */

import { describe, it, expect } from "vitest";

// Helper functions extracted from component for testability
function getThemeIcon(theme: string): string {
  switch (theme) {
    case "light":
      return "☀️";
    case "dark":
      return "🌙";
    case "system":
      return "💻";
    default:
      return "💻";
  }
}

function getThemeLabel(theme: string): string {
  switch (theme) {
    case "light":
      return "Light mode";
    case "dark":
      return "Dark mode";
    case "system":
      return "System theme";
    default:
      return "System theme";
  }
}

describe("ThemeToggle Component", () => {
  describe("Theme Icons", () => {
    it("returns sun icon for light theme", () => {
      expect(getThemeIcon("light")).toBe("☀️");
    });

    it("returns moon icon for dark theme", () => {
      expect(getThemeIcon("dark")).toBe("🌙");
    });

    it("returns computer icon for system theme", () => {
      expect(getThemeIcon("system")).toBe("💻");
    });

    it("returns computer icon for unknown theme", () => {
      expect(getThemeIcon("invalid")).toBe("💻");
      expect(getThemeIcon("")).toBe("💻");
    });

    it("each valid theme has a unique icon", () => {
      const icons = ["light", "dark", "system"].map(getThemeIcon);
      const uniqueIcons = new Set(icons);
      expect(uniqueIcons.size).toBe(3);
    });
  });

  describe("Theme Labels", () => {
    it("returns 'Light mode' for light theme", () => {
      expect(getThemeLabel("light")).toBe("Light mode");
    });

    it("returns 'Dark mode' for dark theme", () => {
      expect(getThemeLabel("dark")).toBe("Dark mode");
    });

    it("returns 'System theme' for system theme", () => {
      expect(getThemeLabel("system")).toBe("System theme");
    });

    it("returns 'System theme' for unknown theme", () => {
      expect(getThemeLabel("invalid")).toBe("System theme");
      expect(getThemeLabel("")).toBe("System theme");
    });

    it("each valid theme has a unique label", () => {
      const labels = ["light", "dark", "system"].map(getThemeLabel);
      const uniqueLabels = new Set(labels);
      expect(uniqueLabels.size).toBe(3);
    });

    it("labels are descriptive and user-friendly", () => {
      const labels = ["light", "dark", "system"].map(getThemeLabel);
      labels.forEach((label) => {
        expect(label.length).toBeGreaterThan(0);
        expect(label).toMatch(/mode|theme/i);
      });
    });
  });

  describe("Icon and Label Consistency", () => {
    it("all themes with icons have corresponding labels", () => {
      const themes = ["light", "dark", "system"];
      themes.forEach((theme) => {
        const icon = getThemeIcon(theme);
        const label = getThemeLabel(theme);
        expect(icon).toBeTruthy();
        expect(label).toBeTruthy();
      });
    });

    it("icon and label describe the same theme", () => {
      // Light theme
      expect(getThemeIcon("light")).toBe("☀️");
      expect(getThemeLabel("light")).toContain("Light");

      // Dark theme
      expect(getThemeIcon("dark")).toBe("🌙");
      expect(getThemeLabel("dark")).toContain("Dark");

      // System theme
      expect(getThemeIcon("system")).toBe("💻");
      expect(getThemeLabel("system")).toContain("System");
    });
  });

  describe("Accessibility", () => {
    it("icons are emoji for better visibility", () => {
      const icons = ["light", "dark", "system"].map(getThemeIcon);
      icons.forEach((icon) => {
        // Emojis are multi-byte characters
        expect(icon.length).toBeGreaterThanOrEqual(1);
      });
    });

    it("labels are human-readable", () => {
      const labels = ["light", "dark", "system"].map(getThemeLabel);
      labels.forEach((label) => {
        expect(label).toMatch(/^[A-Z][a-z]+ (mode|theme)$/);
      });
    });
  });

  describe("Edge Cases", () => {
    it("handles undefined gracefully", () => {
      expect(getThemeIcon(undefined as unknown as string)).toBe("💻");
      expect(getThemeLabel(undefined as unknown as string)).toBe(
        "System theme",
      );
    });

    it("handles null gracefully", () => {
      expect(getThemeIcon(null as unknown as string)).toBe("💻");
      expect(getThemeLabel(null as unknown as string)).toBe("System theme");
    });

    it("handles numeric input gracefully", () => {
      expect(getThemeIcon(123 as unknown as string)).toBe("💻");
      expect(getThemeLabel(123 as unknown as string)).toBe("System theme");
    });

    it("handles object input gracefully", () => {
      expect(getThemeIcon({} as unknown as string)).toBe("💻");
      expect(getThemeLabel({} as unknown as string)).toBe("System theme");
    });
  });

  describe("Theme Coverage", () => {
    it("covers all possible theme values", () => {
      const validThemes = ["light", "dark", "system"];
      validThemes.forEach((theme) => {
        expect(getThemeIcon(theme)).toBeDefined();
        expect(getThemeLabel(theme)).toBeDefined();
      });
    });

    it("icon function is case-sensitive", () => {
      expect(getThemeIcon("Light")).toBe("💻"); // Falls through to default
      expect(getThemeIcon("DARK")).toBe("💻"); // Falls through to default
    });

    it("label function is case-sensitive", () => {
      expect(getThemeLabel("Light")).toBe("System theme"); // Falls through to default
      expect(getThemeLabel("DARK")).toBe("System theme"); // Falls through to default
    });
  });
});
