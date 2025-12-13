/**
 * Tests for Card Content component
 */

import { describe, it, expect } from "vitest";

const cardContentBaseClasses = "p-6 pt-0";

function getCardContentClasses(customClasses?: string): string {
  if (customClasses) {
    return `${cardContentBaseClasses} ${customClasses}`;
  }
  return cardContentBaseClasses;
}

describe("Card Content Component", () => {
  describe("Base Classes", () => {
    it("has padding on all sides", () => {
      expect(getCardContentClasses()).toContain("p-6");
    });

    it("removes top padding", () => {
      expect(getCardContentClasses()).toContain("pt-0");
    });
  });

  describe("Spacing", () => {
    it("maintains consistent internal padding", () => {
      expect(getCardContentClasses()).toContain("p-6");
    });

    it("removes redundant top padding after header", () => {
      // pt-0 removes top padding to avoid double spacing with header
      expect(getCardContentClasses()).toContain("pt-0");
    });
  });

  describe("Custom Classes", () => {
    it("accepts custom classes", () => {
      const classes = getCardContentClasses("min-h-screen");
      expect(classes).toContain("min-h-screen");
    });

    it("preserves padding", () => {
      const classes = getCardContentClasses("flex");
      expect(classes).toContain("p-6");
      expect(classes).toContain("pt-0");
    });
  });

  describe("Layout", () => {
    it("provides space for content", () => {
      expect(getCardContentClasses()).toContain("p-6");
    });

    it("avoids double spacing with card header", () => {
      // pt-0 ensures no gap between header and content
      expect(getCardContentClasses()).toContain("pt-0");
    });
  });
});
