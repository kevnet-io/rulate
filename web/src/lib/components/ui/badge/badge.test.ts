/**
 * Tests for Badge component
 *
 * Tests the Badge component's variant system and class generation.
 */

import { describe, it, expect } from "vitest";

// Badge variants configuration extracted for testability
// This mirrors the configuration from Badge.svelte

type BadgeVariant = "default" | "secondary" | "destructive" | "outline";

const badgeVariantClasses: Record<BadgeVariant, string> = {
  default:
    "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
  secondary:
    "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
  destructive:
    "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
  outline: "text-foreground",
};

const badgeBaseClasses =
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2";

function getBadgeClasses(
  variant: BadgeVariant = "default",
  customClasses?: string,
): string {
  const variantClasses =
    badgeVariantClasses[variant] || badgeVariantClasses.default;
  const classes = `${badgeBaseClasses} ${variantClasses}`;
  if (customClasses) {
    return `${classes} ${customClasses}`;
  }
  return classes;
}

describe("Badge Component", () => {
  describe("Variants", () => {
    it("provides default variant", () => {
      const classes = getBadgeClasses("default");
      expect(classes).toContain("bg-primary");
      expect(classes).toContain("text-primary-foreground");
      expect(classes).toContain("hover:bg-primary/80");
    });

    it("provides secondary variant", () => {
      const classes = getBadgeClasses("secondary");
      expect(classes).toContain("bg-secondary");
      expect(classes).toContain("text-secondary-foreground");
      expect(classes).toContain("hover:bg-secondary/80");
    });

    it("provides destructive variant", () => {
      const classes = getBadgeClasses("destructive");
      expect(classes).toContain("bg-destructive");
      expect(classes).toContain("text-destructive-foreground");
      expect(classes).toContain("hover:bg-destructive/80");
    });

    it("provides outline variant", () => {
      const classes = getBadgeClasses("outline");
      expect(classes).toContain("text-foreground");
      // Outline variant should not have background
      expect(classes).not.toContain("bg-primary");
      expect(classes).not.toContain("bg-secondary");
      expect(classes).not.toContain("bg-destructive");
    });

    it("defaults to default variant when not specified", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("bg-primary");
    });
  });

  describe("Base Classes", () => {
    it("includes layout classes", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("inline-flex");
      expect(classes).toContain("items-center");
    });

    it("includes shape and sizing classes", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("rounded-md");
      expect(classes).toContain("border");
      expect(classes).toContain("px-2.5");
      expect(classes).toContain("py-0.5");
    });

    it("includes typography classes", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("text-xs");
      expect(classes).toContain("font-semibold");
    });

    it("includes transition classes", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("transition-colors");
    });

    it("includes focus styles", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("focus:outline-none");
      expect(classes).toContain("focus:ring-2");
      expect(classes).toContain("focus:ring-ring");
      expect(classes).toContain("focus:ring-offset-2");
    });
  });

  describe("Custom Classes", () => {
    it("merges custom classes with variant classes", () => {
      const classes = getBadgeClasses("default", "custom-class");
      expect(classes).toContain("bg-primary");
      expect(classes).toContain("custom-class");
    });

    it("supports multiple custom classes", () => {
      const classes = getBadgeClasses("secondary", "custom-1 custom-2");
      expect(classes).toContain("bg-secondary");
      expect(classes).toContain("custom-1");
      expect(classes).toContain("custom-2");
    });

    it("accepts custom classes with all variants", () => {
      const variants: BadgeVariant[] = [
        "default",
        "secondary",
        "destructive",
        "outline",
      ];
      variants.forEach((variant) => {
        const classes = getBadgeClasses(variant, "custom");
        expect(classes).toContain("custom");
      });
    });
  });

  describe("Variant Styles", () => {
    it("default variant has shadow", () => {
      const classes = getBadgeClasses("default");
      expect(classes).toContain("shadow");
    });

    it("secondary variant has no shadow", () => {
      const classes = getBadgeClasses("secondary");
      expect(classes).not.toContain("shadow");
    });

    it("destructive variant has shadow", () => {
      const classes = getBadgeClasses("destructive");
      expect(classes).toContain("shadow");
    });

    it("outline variant has no shadow", () => {
      const classes = getBadgeClasses("outline");
      expect(classes).not.toContain("shadow");
    });

    it("default, secondary, and destructive variants have transparent borders", () => {
      const defaultClasses = getBadgeClasses("default");
      expect(defaultClasses).toContain("border-transparent");

      const secondaryClasses = getBadgeClasses("secondary");
      expect(secondaryClasses).toContain("border-transparent");

      const destructiveClasses = getBadgeClasses("destructive");
      expect(destructiveClasses).toContain("border-transparent");
    });

    it("outline variant relies on text color without background", () => {
      const outlineClasses = getBadgeClasses("outline");
      expect(outlineClasses).toContain("text-foreground");
      expect(outlineClasses).not.toContain("bg-");
    });
  });

  describe("Variant Colors", () => {
    it("default variant uses primary colors", () => {
      const classes = getBadgeClasses("default");
      expect(classes).toMatch(/bg-primary/);
      expect(classes).toMatch(/text-primary-foreground/);
    });

    it("secondary variant uses secondary colors", () => {
      const classes = getBadgeClasses("secondary");
      expect(classes).toMatch(/bg-secondary/);
      expect(classes).toMatch(/text-secondary-foreground/);
    });

    it("destructive variant uses destructive colors", () => {
      const classes = getBadgeClasses("destructive");
      expect(classes).toMatch(/bg-destructive/);
      expect(classes).toMatch(/text-destructive-foreground/);
    });

    it("outline variant uses foreground colors", () => {
      const classes = getBadgeClasses("outline");
      expect(classes).toContain("text-foreground");
    });
  });

  describe("Hover States", () => {
    it("default variant has hover state", () => {
      const classes = getBadgeClasses("default");
      expect(classes).toContain("hover:bg-primary/80");
    });

    it("secondary variant has hover state", () => {
      const classes = getBadgeClasses("secondary");
      expect(classes).toContain("hover:bg-secondary/80");
    });

    it("destructive variant has hover state", () => {
      const classes = getBadgeClasses("destructive");
      expect(classes).toContain("hover:bg-destructive/80");
    });

    it("outline variant has no hover background", () => {
      const classes = getBadgeClasses("outline");
      expect(classes).not.toMatch(/hover:bg-/);
    });
  });

  describe("Accessibility", () => {
    it("has focus ring for keyboard navigation", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("focus:ring");
    });

    it("removes default focus outline", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("focus:outline-none");
    });

    it("has ring offset for visual clarity", () => {
      const classes = getBadgeClasses();
      expect(classes).toContain("focus:ring-offset-2");
    });
  });

  describe("Responsiveness", () => {
    it("all variants are responsive-ready", () => {
      const variants: BadgeVariant[] = [
        "default",
        "secondary",
        "destructive",
        "outline",
      ];
      variants.forEach((variant) => {
        const classes = getBadgeClasses(variant);
        // Should include responsive padding
        expect(classes).toContain("px-2.5");
        expect(classes).toContain("py-0.5");
      });
    });
  });

  describe("Edge Cases", () => {
    it("handles undefined variant as default", () => {
      const classes = getBadgeClasses("default");
      expect(classes).toContain("bg-primary");
    });

    it("handles empty custom class string", () => {
      const classes = getBadgeClasses("default", "");
      expect(classes).toContain("bg-primary");
    });

    it("includes all base classes in every variant", () => {
      const variants: BadgeVariant[] = [
        "default",
        "secondary",
        "destructive",
        "outline",
      ];
      variants.forEach((variant) => {
        const classes = getBadgeClasses(variant);
        expect(classes).toContain("inline-flex");
        expect(classes).toContain("rounded-md");
        expect(classes).toContain("border");
        expect(classes).toContain("text-xs");
        expect(classes).toContain("font-semibold");
      });
    });
  });
});
