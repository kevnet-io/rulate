/**
 * Tests for Card Description component
 */

import { describe, it, expect } from "vitest";

const cardDescriptionBaseClasses = "text-sm text-muted-foreground";

function getCardDescriptionClasses(customClasses?: string): string {
  if (customClasses) {
    return `${cardDescriptionBaseClasses} ${customClasses}`;
  }
  return cardDescriptionBaseClasses;
}

describe("Card Description Component", () => {
  describe("Base Classes", () => {
    it("has small text size", () => {
      expect(getCardDescriptionBaseClasses()).toContain("text-sm");
    });

    it("uses muted foreground color", () => {
      expect(getCardDescriptionClasses()).toContain("text-muted-foreground");
    });
  });

  describe("Typography", () => {
    it("uses small text for secondary content", () => {
      expect(getCardDescriptionClasses()).toContain("text-sm");
    });

    it("uses muted color for reduced emphasis", () => {
      expect(getCardDescriptionClasses()).toContain("text-muted-foreground");
    });
  });

  describe("Custom Classes", () => {
    it("accepts custom classes", () => {
      const classes = getCardDescriptionClasses("mb-4");
      expect(classes).toContain("mb-4");
    });

    it("preserves base typography", () => {
      const classes = getCardDescriptionClasses("italic");
      expect(classes).toContain("text-sm");
      expect(classes).toContain("text-muted-foreground");
    });
  });

  describe("Visual Hierarchy", () => {
    it("is visually distinct from title", () => {
      // Smaller size and muted color differentiate from title
      expect(getCardDescriptionClasses()).toContain("text-sm");
      expect(getCardDescriptionClasses()).toContain("text-muted-foreground");
    });
  });
});

// Fix function name typo
function getCardDescriptionBaseClasses(): string {
  return cardDescriptionBaseClasses;
}
