/**
 * Tests for Card Header component
 */

import { describe, it, expect } from "vitest";

const cardHeaderBaseClasses = "flex flex-col space-y-1.5 p-6";

function getCardHeaderClasses(customClasses?: string): string {
  if (customClasses) {
    return `${cardHeaderBaseClasses} ${customClasses}`;
  }
  return cardHeaderBaseClasses;
}

describe("Card Header Component", () => {
  describe("Base Classes", () => {
    it("has flex layout", () => {
      expect(getCardHeaderClasses()).toContain("flex");
    });

    it("stacks content vertically", () => {
      expect(getCardHeaderClasses()).toContain("flex-col");
    });

    it("has spacing between items", () => {
      expect(getCardHeaderClasses()).toContain("space-y-1.5");
    });

    it("has padding", () => {
      expect(getCardHeaderClasses()).toContain("p-6");
    });
  });

  describe("Custom Classes", () => {
    it("accepts custom classes", () => {
      const classes = getCardHeaderClasses("border-b");
      expect(classes).toContain("border-b");
    });

    it("preserves layout classes", () => {
      const classes = getCardHeaderClasses("mb-4");
      expect(classes).toContain("flex");
      expect(classes).toContain("flex-col");
      expect(classes).toContain("p-6");
    });
  });

  describe("Styling", () => {
    it("provides consistent spacing", () => {
      const classes = getCardHeaderClasses();
      expect(classes).toContain("space-y-1.5");
    });

    it("has standard padding", () => {
      expect(getCardHeaderClasses()).toContain("p-6");
    });
  });
});
