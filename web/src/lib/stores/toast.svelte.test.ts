/**
 * Tests for toast store
 *
 * Tests the toast notification store for adding, removing, and auto-dismissing toasts.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { toastStore } from './toast.svelte';

describe('Toast Store', () => {
	beforeEach(() => {
		// Clear all toasts before each test
		toastStore.clear();
		// Use fake timers for auto-dismiss testing
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('Adding Toasts', () => {
		it('adds a toast with success type', () => {
			toastStore.success('Success message');
			const toasts = toastStore.getToasts();

			expect(toasts).toHaveLength(1);
			expect(toasts[0].message).toBe('Success message');
			expect(toasts[0].type).toBe('success');
		});

		it('adds a toast with error type', () => {
			toastStore.error('Error message');
			const toasts = toastStore.getToasts();

			expect(toasts).toHaveLength(1);
			expect(toasts[0].message).toBe('Error message');
			expect(toasts[0].type).toBe('error');
		});

		it('adds a toast with warning type', () => {
			toastStore.warning('Warning message');
			const toasts = toastStore.getToasts();

			expect(toasts).toHaveLength(1);
			expect(toasts[0].message).toBe('Warning message');
			expect(toasts[0].type).toBe('warning');
		});

		it('adds a toast with info type', () => {
			toastStore.info('Info message');
			const toasts = toastStore.getToasts();

			expect(toasts).toHaveLength(1);
			expect(toasts[0].message).toBe('Info message');
			expect(toasts[0].type).toBe('info');
		});

		it('generates unique IDs for each toast', () => {
			toastStore.success('First');
			toastStore.success('Second');
			toastStore.success('Third');

			const toasts = toastStore.getToasts();
			const ids = toasts.map(t => t.id);

			expect(ids).toHaveLength(3);
			expect(new Set(ids).size).toBe(3); // All unique
		});

		it('allows multiple toasts to stack', () => {
			toastStore.success('First');
			toastStore.error('Second');
			toastStore.warning('Third');

			const toasts = toastStore.getToasts();
			expect(toasts).toHaveLength(3);
		});

		it('uses default duration when not specified', () => {
			toastStore.success('Test');
			const toasts = toastStore.getToasts();

			expect(toasts[0].duration).toBe(5000);
		});

		it('accepts custom duration', () => {
			toastStore.success('Test', 10000);
			const toasts = toastStore.getToasts();

			expect(toasts[0].duration).toBe(10000);
		});
	});

	describe('Removing Toasts', () => {
		it('removes a toast by ID', () => {
			toastStore.success('First');
			toastStore.success('Second');

			const toasts = toastStore.getToasts();
			const firstId = toasts[0].id;

			toastStore.remove(firstId);

			const remaining = toastStore.getToasts();
			expect(remaining).toHaveLength(1);
			expect(remaining[0].message).toBe('Second');
		});

		it('does nothing when removing non-existent ID', () => {
			toastStore.success('First');
			toastStore.remove('non-existent-id');

			const toasts = toastStore.getToasts();
			expect(toasts).toHaveLength(1);
		});

		it('clears all toasts', () => {
			toastStore.success('First');
			toastStore.error('Second');
			toastStore.warning('Third');

			toastStore.clear();

			const toasts = toastStore.getToasts();
			expect(toasts).toHaveLength(0);
		});
	});

	describe('Auto-dismiss', () => {
		it('auto-dismisses toast after duration', () => {
			toastStore.success('Test', 3000);

			expect(toastStore.getToasts()).toHaveLength(1);

			// Fast-forward time by 3000ms
			vi.advanceTimersByTime(3000);

			expect(toastStore.getToasts()).toHaveLength(0);
		});

		it('auto-dismisses multiple toasts independently', () => {
			toastStore.success('First', 2000);
			toastStore.success('Second', 4000);

			expect(toastStore.getToasts()).toHaveLength(2);

			// After 2s, first should be gone
			vi.advanceTimersByTime(2000);
			expect(toastStore.getToasts()).toHaveLength(1);
			expect(toastStore.getToasts()[0].message).toBe('Second');

			// After another 2s, second should be gone
			vi.advanceTimersByTime(2000);
			expect(toastStore.getToasts()).toHaveLength(0);
		});

		it('does not auto-dismiss when duration is 0', () => {
			toastStore.success('Persistent', 0);

			expect(toastStore.getToasts()).toHaveLength(1);

			// Fast-forward time significantly
			vi.advanceTimersByTime(10000);

			// Should still be there
			expect(toastStore.getToasts()).toHaveLength(1);
		});

		it('cancels auto-dismiss when manually removed', () => {
			toastStore.success('Test', 5000);
			const toasts = toastStore.getToasts();
			const id = toasts[0].id;

			// Manually remove before timeout
			toastStore.remove(id);

			// Fast-forward time
			vi.advanceTimersByTime(5000);

			// Should remain empty (no double-removal issues)
			expect(toastStore.getToasts()).toHaveLength(0);
		});
	});

	describe('Toast Order', () => {
		it('adds new toasts to the end', () => {
			toastStore.success('First');
			toastStore.error('Second');
			toastStore.warning('Third');

			const toasts = toastStore.getToasts();
			expect(toasts[0].message).toBe('First');
			expect(toasts[1].message).toBe('Second');
			expect(toasts[2].message).toBe('Third');
		});

		it('maintains order when removing from middle', () => {
			toastStore.success('First');
			toastStore.error('Second');
			toastStore.warning('Third');

			const toasts = toastStore.getToasts();
			toastStore.remove(toasts[1].id);

			const remaining = toastStore.getToasts();
			expect(remaining).toHaveLength(2);
			expect(remaining[0].message).toBe('First');
			expect(remaining[1].message).toBe('Third');
		});
	});

	describe('Toast Content', () => {
		it('preserves message content exactly', () => {
			const message = 'Complex message with "quotes" and special chars: !@#$%';
			toastStore.success(message);

			const toasts = toastStore.getToasts();
			expect(toasts[0].message).toBe(message);
		});

		it('handles empty messages', () => {
			toastStore.success('');
			const toasts = toastStore.getToasts();

			expect(toasts).toHaveLength(1);
			expect(toasts[0].message).toBe('');
		});

		it('handles long messages', () => {
			const longMessage = 'A'.repeat(500);
			toastStore.success(longMessage);

			const toasts = toastStore.getToasts();
			expect(toasts[0].message).toBe(longMessage);
		});
	});

	describe('Edge Cases', () => {
		it('handles rapid successive additions', () => {
			for (let i = 0; i < 10; i++) {
				toastStore.success(`Toast ${i}`);
			}

			const toasts = toastStore.getToasts();
			expect(toasts).toHaveLength(10);
		});

		it('handles clearing empty toast list', () => {
			toastStore.clear();
			toastStore.clear();

			expect(toastStore.getToasts()).toHaveLength(0);
		});

		it('handles removing same ID multiple times', () => {
			toastStore.success('Test');
			const id = toastStore.getToasts()[0].id;

			toastStore.remove(id);
			toastStore.remove(id);
			toastStore.remove(id);

			expect(toastStore.getToasts()).toHaveLength(0);
		});

		it('handles negative duration as 0 (no auto-dismiss)', () => {
			toastStore.success('Test', -1000);

			vi.advanceTimersByTime(10000);

			// Should not auto-dismiss with negative duration
			expect(toastStore.getToasts()).toHaveLength(1);
		});
	});

	describe('Type Safety', () => {
		it('toast has correct structure', () => {
			toastStore.success('Test', 3000);
			const toast = toastStore.getToasts()[0];

			expect(toast).toHaveProperty('id');
			expect(toast).toHaveProperty('message');
			expect(toast).toHaveProperty('type');
			expect(toast).toHaveProperty('duration');

			expect(typeof toast.id).toBe('string');
			expect(typeof toast.message).toBe('string');
			expect(typeof toast.type).toBe('string');
			expect(typeof toast.duration).toBe('number');
		});

		it('getToasts returns array', () => {
			const toasts = toastStore.getToasts();
			expect(Array.isArray(toasts)).toBe(true);
		});
	});
});
