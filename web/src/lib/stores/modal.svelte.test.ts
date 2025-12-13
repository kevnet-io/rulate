/**
 * Tests for modal store
 *
 * Tests the modal confirmation store for opening, closing, and promise-based confirmations.
 */

import { describe, it, expect, beforeEach } from "vitest";
import { modalStore } from "./modal.svelte";

describe("Modal Store", () => {
  beforeEach(() => {
    // Close modal before each test
    modalStore.close();
  });

  describe("Opening and Closing", () => {
    it("starts closed", () => {
      expect(modalStore.isOpen).toBe(false);
      expect(modalStore.data).toBeNull();
    });

    it("opens modal with data", () => {
      modalStore.open({
        title: "Test Modal",
        message: "Test message",
      });

      expect(modalStore.isOpen).toBe(true);
      expect(modalStore.data).not.toBeNull();
      expect(modalStore.data?.title).toBe("Test Modal");
      expect(modalStore.data?.message).toBe("Test message");
    });

    it("closes modal", () => {
      modalStore.open({
        title: "Test Modal",
        message: "Test message",
      });

      expect(modalStore.isOpen).toBe(true);

      modalStore.close();

      expect(modalStore.isOpen).toBe(false);
      expect(modalStore.data).toBeNull();
    });

    it("clears data when closing", () => {
      modalStore.open({
        title: "Test Modal",
        message: "Test message",
        confirmText: "OK",
        isDanger: true,
      });

      modalStore.close();

      expect(modalStore.data).toBeNull();
    });
  });

  describe("Modal Data", () => {
    it("stores title and message", () => {
      modalStore.open({
        title: "Delete Item",
        message: "Are you sure you want to delete this item?",
      });

      expect(modalStore.data?.title).toBe("Delete Item");
      expect(modalStore.data?.message).toBe(
        "Are you sure you want to delete this item?",
      );
    });

    it("stores custom confirm text", () => {
      modalStore.open({
        title: "Confirm",
        message: "Proceed?",
        confirmText: "Yes, proceed",
      });

      expect(modalStore.data?.confirmText).toBe("Yes, proceed");
    });

    it("stores custom cancel text", () => {
      modalStore.open({
        title: "Confirm",
        message: "Proceed?",
        cancelText: "No, go back",
      });

      expect(modalStore.data?.cancelText).toBe("No, go back");
    });

    it("stores isDanger flag", () => {
      modalStore.open({
        title: "Delete",
        message: "This is dangerous",
        isDanger: true,
      });

      expect(modalStore.data?.isDanger).toBe(true);
    });

    it("isDanger defaults to undefined when not set", () => {
      modalStore.open({
        title: "Confirm",
        message: "Safe action",
      });

      expect(modalStore.data?.isDanger).toBeUndefined();
    });
  });

  describe("Confirmation Flow", () => {
    it("confirm() returns a promise", () => {
      const promise = modalStore.confirm({
        title: "Confirm",
        message: "Proceed?",
      });

      expect(promise).toBeInstanceOf(Promise);
    });

    it("opens modal when confirm() is called", () => {
      modalStore.confirm({
        title: "Confirm",
        message: "Proceed?",
      });

      expect(modalStore.isOpen).toBe(true);
      expect(modalStore.data?.title).toBe("Confirm");
    });

    it("resolves promise with true when confirmed", async () => {
      const promise = modalStore.confirm({
        title: "Confirm",
        message: "Proceed?",
      });

      // Simulate user clicking confirm
      modalStore.handleConfirm();

      const result = await promise;
      expect(result).toBe(true);
    });

    it("resolves promise with false when cancelled", async () => {
      const promise = modalStore.confirm({
        title: "Confirm",
        message: "Proceed?",
      });

      // Simulate user clicking cancel
      modalStore.handleCancel();

      const result = await promise;
      expect(result).toBe(false);
    });

    it("closes modal after confirmation", async () => {
      const promise = modalStore.confirm({
        title: "Confirm",
        message: "Proceed?",
      });

      expect(modalStore.isOpen).toBe(true);

      modalStore.handleConfirm();
      await promise;

      expect(modalStore.isOpen).toBe(false);
    });

    it("closes modal after cancellation", async () => {
      const promise = modalStore.confirm({
        title: "Confirm",
        message: "Proceed?",
      });

      expect(modalStore.isOpen).toBe(true);

      modalStore.handleCancel();
      await promise;

      expect(modalStore.isOpen).toBe(false);
    });
  });

  describe("Multiple Confirmations", () => {
    it("replaces previous modal when opening new one", () => {
      modalStore.open({
        title: "First",
        message: "First message",
      });

      modalStore.open({
        title: "Second",
        message: "Second message",
      });

      expect(modalStore.data?.title).toBe("Second");
      expect(modalStore.data?.message).toBe("Second message");
    });

    it("handles sequential confirmations", async () => {
      const promise1 = modalStore.confirm({
        title: "First",
        message: "First confirmation",
      });

      modalStore.handleConfirm();
      const result1 = await promise1;

      const promise2 = modalStore.confirm({
        title: "Second",
        message: "Second confirmation",
      });

      modalStore.handleCancel();
      const result2 = await promise2;

      expect(result1).toBe(true);
      expect(result2).toBe(false);
    });
  });

  describe("Edge Cases", () => {
    it("handleConfirm does nothing when no resolver", () => {
      modalStore.open({
        title: "Test",
        message: "Test",
      });

      // Should not throw
      expect(() => modalStore.handleConfirm()).not.toThrow();
    });

    it("handleCancel does nothing when no resolver", () => {
      modalStore.open({
        title: "Test",
        message: "Test",
      });

      // Should not throw
      expect(() => modalStore.handleCancel()).not.toThrow();
    });

    it("close() is idempotent", () => {
      modalStore.close();
      modalStore.close();
      modalStore.close();

      expect(modalStore.isOpen).toBe(false);
    });

    it("handles empty strings in data", () => {
      modalStore.open({
        title: "",
        message: "",
        confirmText: "",
        cancelText: "",
      });

      expect(modalStore.data?.title).toBe("");
      expect(modalStore.data?.message).toBe("");
      expect(modalStore.data?.confirmText).toBe("");
      expect(modalStore.data?.cancelText).toBe("");
    });

    it("handles long text content", () => {
      const longTitle = "A".repeat(500);
      const longMessage = "B".repeat(1000);

      modalStore.open({
        title: longTitle,
        message: longMessage,
      });

      expect(modalStore.data?.title).toBe(longTitle);
      expect(modalStore.data?.message).toBe(longMessage);
    });

    it("handles special characters in text", () => {
      const specialChars = "!@#$%^&*()[]{}|\\<>?/~`\"'";

      modalStore.open({
        title: specialChars,
        message: specialChars,
      });

      expect(modalStore.data?.title).toBe(specialChars);
      expect(modalStore.data?.message).toBe(specialChars);
    });
  });

  describe("State Transitions", () => {
    it("transitions from closed -> open -> closed", () => {
      expect(modalStore.isOpen).toBe(false);

      modalStore.open({
        title: "Test",
        message: "Test",
      });
      expect(modalStore.isOpen).toBe(true);

      modalStore.close();
      expect(modalStore.isOpen).toBe(false);
    });

    it("transitions through multiple open states", () => {
      modalStore.open({
        title: "First",
        message: "First",
      });
      expect(modalStore.data?.title).toBe("First");

      modalStore.open({
        title: "Second",
        message: "Second",
      });
      expect(modalStore.data?.title).toBe("Second");

      modalStore.close();
      expect(modalStore.isOpen).toBe(false);
    });
  });

  describe("Promise Behavior", () => {
    it("each confirm() creates a new promise", () => {
      const promise1 = modalStore.confirm({
        title: "First",
        message: "First",
      });

      modalStore.handleConfirm();

      const promise2 = modalStore.confirm({
        title: "Second",
        message: "Second",
      });

      expect(promise1).not.toBe(promise2);
    });

    it("promises resolve independently", async () => {
      const promise1 = modalStore.confirm({
        title: "First",
        message: "First",
      });

      modalStore.handleConfirm();
      const result1 = await promise1;

      const promise2 = modalStore.confirm({
        title: "Second",
        message: "Second",
      });

      modalStore.handleCancel();
      const result2 = await promise2;

      expect(result1).toBe(true);
      expect(result2).toBe(false);
    });
  });
});
