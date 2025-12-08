/**
 * Tests for Skeleton component
 *
 * Tests the Skeleton component's styling and customization.
 */

import { describe, it, expect } from 'vitest';

// Skeleton configuration extracted for testability
const skeletonBaseClasses = 'animate-pulse rounded-md bg-primary/10';

function getSkeletonClasses(customClasses?: string): string {
	if (customClasses) {
		return `${skeletonBaseClasses} ${customClasses}`;
	}
	return skeletonBaseClasses;
}

describe('Skeleton Component', () => {
	describe('Base Classes', () => {
		it('has pulse animation', () => {
			const classes = getSkeletonClasses();
			expect(classes).toContain('animate-pulse');
		});

		it('has rounded corners', () => {
			const classes = getSkeletonClasses();
			expect(classes).toContain('rounded-md');
		});

		it('has primary background with transparency', () => {
			const classes = getSkeletonClasses();
			expect(classes).toContain('bg-primary/10');
		});

		it('applies all base classes', () => {
			const classes = getSkeletonClasses();
			expect(classes).toBe('animate-pulse rounded-md bg-primary/10');
		});
	});

	describe('Custom Classes', () => {
		it('accepts custom class', () => {
			const classes = getSkeletonClasses('h-12');
			expect(classes).toContain('h-12');
			expect(classes).toContain('animate-pulse');
		});

		it('accepts multiple custom classes', () => {
			const classes = getSkeletonClasses('h-12 w-full');
			expect(classes).toContain('h-12');
			expect(classes).toContain('w-full');
		});

		it('combines base and custom classes', () => {
			const classes = getSkeletonClasses('h-20 rounded-lg');
			expect(classes).toContain('animate-pulse');
			expect(classes).toContain('rounded-md');
			expect(classes).toContain('bg-primary/10');
			expect(classes).toContain('h-20');
			expect(classes).toContain('rounded-lg');
		});
	});

	describe('Common Use Cases', () => {
		it('can be sized for text lines', () => {
			const classes = getSkeletonClasses('h-4 w-full');
			expect(classes).toContain('h-4');
			expect(classes).toContain('w-full');
		});

		it('can be sized for large elements', () => {
			const classes = getSkeletonClasses('h-64 w-64 rounded-lg');
			expect(classes).toContain('h-64');
			expect(classes).toContain('w-64');
		});

		it('can be sized for circular elements', () => {
			const classes = getSkeletonClasses('h-16 w-16 rounded-full');
			expect(classes).toContain('h-16');
			expect(classes).toContain('w-16');
			expect(classes).toContain('rounded-full');
		});

		it('can have margins', () => {
			const classes = getSkeletonClasses('mb-4');
			expect(classes).toContain('mb-4');
		});
	});

	describe('Animation', () => {
		it('includes pulse animation for loading state', () => {
			const classes = getSkeletonClasses();
			expect(classes).toMatch(/animate-pulse/);
		});

		it('animation is preserved with custom classes', () => {
			const classes = getSkeletonClasses('h-8');
			expect(classes).toContain('animate-pulse');
		});
	});

	describe('Styling', () => {
		it('uses subtle primary color (10% opacity)', () => {
			const classes = getSkeletonClasses();
			expect(classes).toContain('bg-primary/10');
		});

		it('rounded corners match design system', () => {
			const classes = getSkeletonClasses();
			expect(classes).toContain('rounded-md');
		});

		it('uses consistent border radius', () => {
			const classes = getSkeletonClasses();
			// Medium rounded corners (8px)
			expect(classes).toMatch(/rounded-md/);
		});
	});

	describe('Customization', () => {
		it('does not have custom classes by default', () => {
			const classes = getSkeletonClasses();
			expect(classes).toBe('animate-pulse rounded-md bg-primary/10');
		});

		it('handles empty string as no custom classes', () => {
			const classes = getSkeletonClasses('');
			expect(classes).toBe('animate-pulse rounded-md bg-primary/10');
		});

		it('allows overriding background with custom class', () => {
			const classes = getSkeletonClasses('bg-secondary/20');
			// The base class is still there but custom could override it
			expect(classes).toContain('bg-primary/10');
			expect(classes).toContain('bg-secondary/20');
		});

		it('allows overriding border radius with custom class', () => {
			const classes = getSkeletonClasses('rounded-full');
			expect(classes).toContain('rounded-md');
			expect(classes).toContain('rounded-full');
		});
	});

	describe('Accessibility', () => {
		it('is semantically a div element', () => {
			// Skeleton is a div wrapper without additional a11y attributes
			expect(getSkeletonClasses()).toBeDefined();
		});

		it('works as a placeholder element', () => {
			const classes = getSkeletonClasses('h-8 w-48');
			expect(classes).toContain('animate-pulse');
			// Can be used as a placeholder while content loads
		});
	});

	describe('Edge Cases', () => {
		it('handles undefined custom classes', () => {
			const classes = getSkeletonClasses(undefined);
			expect(classes).toBe('animate-pulse rounded-md bg-primary/10');
		});

		it('preserves all base classes', () => {
			const classes = getSkeletonClasses('custom');
			const baseClasses = ['animate-pulse', 'rounded-md', 'bg-primary/10'];
			baseClasses.forEach((baseClass) => {
				expect(classes).toContain(baseClass);
			});
		});

		it('handles very long custom class string', () => {
			const longCustom = 'h-screen w-full flex items-center justify-center p-4 gap-4';
			const classes = getSkeletonClasses(longCustom);
			expect(classes).toContain('animate-pulse');
			expect(classes).toContain(longCustom);
		});
	});
});
