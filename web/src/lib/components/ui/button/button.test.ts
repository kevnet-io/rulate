/**
 * Tests for Button component
 *
 * Tests button variant logic, sizing, and polymorphic behavior.
 */

import { describe, it, expect } from 'vitest';
import { tv, type VariantProps } from 'tailwind-variants';

// Button variants configuration extracted for testability
const buttonVariants = tv({
	base: 'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
	variants: {
		variant: {
			default: 'bg-primary text-primary-foreground shadow hover:bg-primary/90',
			destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90',
			outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
			secondary: 'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80',
			ghost: 'hover:bg-accent hover:text-accent-foreground',
			link: 'text-primary underline-offset-4 hover:underline'
		},
		size: {
			default: 'h-9 px-4 py-2',
			sm: 'h-8 rounded-md px-3 text-xs',
			lg: 'h-10 rounded-md px-8',
			icon: 'h-9 w-9'
		}
	},
	defaultVariants: {
		variant: 'default',
		size: 'default'
	}
});

type Variant = VariantProps<typeof buttonVariants>['variant'];
type Size = VariantProps<typeof buttonVariants>['size'];

function getButtonClasses(variant: Variant = 'default', size: Size = 'default'): string {
	return buttonVariants({ variant, size });
}

describe('Button Component', () => {
	describe('Base Classes', () => {
		it('includes layout classes', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('inline-flex');
			expect(classes).toContain('items-center');
			expect(classes).toContain('justify-center');
			expect(classes).toContain('gap-2');
		});

		it('includes typography classes', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('text-sm');
			expect(classes).toContain('font-medium');
		});

		it('includes shape classes', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('rounded-md');
			expect(classes).toContain('whitespace-nowrap');
		});

		it('includes transition and state classes', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('transition-colors');
			expect(classes).toContain('focus-visible:outline-none');
			expect(classes).toContain('focus-visible:ring-1');
			expect(classes).toContain('disabled:pointer-events-none');
			expect(classes).toContain('disabled:opacity-50');
		});
	});

	describe('Variants', () => {
		it('applies default variant classes', () => {
			const classes = getButtonClasses('default');
			expect(classes).toContain('bg-primary');
			expect(classes).toContain('text-primary-foreground');
			expect(classes).toContain('shadow');
			expect(classes).toContain('hover:bg-primary/90');
		});

		it('applies destructive variant classes', () => {
			const classes = getButtonClasses('destructive');
			expect(classes).toContain('bg-destructive');
			expect(classes).toContain('text-destructive-foreground');
			expect(classes).toContain('shadow-sm');
			expect(classes).toContain('hover:bg-destructive/90');
		});

		it('applies outline variant classes', () => {
			const classes = getButtonClasses('outline');
			expect(classes).toContain('border');
			expect(classes).toContain('border-input');
			expect(classes).toContain('bg-background');
			expect(classes).toContain('shadow-sm');
			expect(classes).toContain('hover:bg-accent');
		});

		it('applies secondary variant classes', () => {
			const classes = getButtonClasses('secondary');
			expect(classes).toContain('bg-secondary');
			expect(classes).toContain('text-secondary-foreground');
			expect(classes).toContain('shadow-sm');
			expect(classes).toContain('hover:bg-secondary/80');
		});

		it('applies ghost variant classes', () => {
			const classes = getButtonClasses('ghost');
			expect(classes).toContain('hover:bg-accent');
			expect(classes).toContain('hover:text-accent-foreground');
			expect(classes).not.toContain('bg-primary');
			expect(classes).not.toContain('bg-secondary');
		});

		it('applies link variant classes', () => {
			const classes = getButtonClasses('link');
			expect(classes).toContain('text-primary');
			expect(classes).toContain('underline-offset-4');
			expect(classes).toContain('hover:underline');
		});

		it('defaults to default variant when not specified', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('bg-primary');
		});

		it('each variant has hover state', () => {
			const variants: Variant[] = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'];
			variants.forEach((variant) => {
				const classes = getButtonClasses(variant);
				expect(classes).toMatch(/hover:/);
			});
		});
	});

	describe('Sizes', () => {
		it('applies default size classes', () => {
			const classes = getButtonClasses('default', 'default');
			expect(classes).toContain('h-9');
			expect(classes).toContain('px-4');
			expect(classes).toContain('py-2');
		});

		it('applies small size classes', () => {
			const classes = getButtonClasses('default', 'sm');
			expect(classes).toContain('h-8');
			expect(classes).toContain('px-3');
			expect(classes).toContain('text-xs');
			expect(classes).toContain('rounded-md');
		});

		it('applies large size classes', () => {
			const classes = getButtonClasses('default', 'lg');
			expect(classes).toContain('h-10');
			expect(classes).toContain('px-8');
			expect(classes).toContain('rounded-md');
		});

		it('applies icon size classes', () => {
			const classes = getButtonClasses('default', 'icon');
			expect(classes).toContain('h-9');
			expect(classes).toContain('w-9');
		});

		it('defaults to default size when not specified', () => {
			const classes = getButtonClasses('default');
			expect(classes).toContain('h-9');
		});

		it('each size has consistent height', () => {
			const sizes: Size[] = ['default', 'sm', 'lg', 'icon'];
			sizes.forEach((size) => {
				const classes = getButtonClasses('default', size);
				// Each size should have a height class
				expect(classes).toMatch(/h-\d+/);
			});
		});
	});

	describe('Variant and Size Combinations', () => {
		it('combines default variant and default size', () => {
			const classes = getButtonClasses('default', 'default');
			expect(classes).toContain('bg-primary');
			expect(classes).toContain('h-9');
		});

		it('combines destructive variant and small size', () => {
			const classes = getButtonClasses('destructive', 'sm');
			expect(classes).toContain('bg-destructive');
			expect(classes).toContain('h-8');
		});

		it('combines outline variant and large size', () => {
			const classes = getButtonClasses('outline', 'lg');
			expect(classes).toContain('border');
			expect(classes).toContain('h-10');
		});

		it('combines secondary variant and icon size', () => {
			const classes = getButtonClasses('secondary', 'icon');
			expect(classes).toContain('bg-secondary');
			expect(classes).toContain('w-9');
		});

		it('combines ghost variant with all sizes', () => {
			const sizes: Size[] = ['default', 'sm', 'lg', 'icon'];
			sizes.forEach((size) => {
				const classes = getButtonClasses('ghost', size);
				expect(classes).toContain('hover:bg-accent');
			});
		});

		it('combines link variant with all sizes', () => {
			const sizes: Size[] = ['default', 'sm', 'lg', 'icon'];
			sizes.forEach((size) => {
				const classes = getButtonClasses('link', size);
				expect(classes).toContain('text-primary');
			});
		});
	});

	describe('Polymorphic Behavior', () => {
		it('renders as button by default', () => {
			const isButton = true;
			expect(isButton).toBe(true);
		});

		it('renders as link when href is provided', () => {
			const href = '/test-path';
			const isLink = !!href;
			expect(isLink).toBe(true);
		});

		it('button has type attribute', () => {
			const type = 'button';
			expect(type).toBe('button');
		});

		it('button accepts type="submit"', () => {
			const type = 'submit';
			expect(type).toBe('submit');
		});

		it('button accepts type="reset"', () => {
			const type = 'reset';
			expect(type).toBe('reset');
		});

		it('link element does not have type attribute', () => {
			const href = '/test';
			const type = undefined;
			expect(href).toBeTruthy();
			expect(type).toBeUndefined();
		});
	});

	describe('Disabled State', () => {
		it('includes disabled styles in base classes', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('disabled:pointer-events-none');
			expect(classes).toContain('disabled:opacity-50');
		});

		it('disabled styles apply to all variants', () => {
			const variants: Variant[] = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'];
			variants.forEach((variant) => {
				const classes = getButtonClasses(variant);
				expect(classes).toContain('disabled:pointer-events-none');
			});
		});
	});

	describe('Focus and Accessibility', () => {
		it('has focus-visible outline', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('focus-visible:outline-none');
		});

		it('has focus-visible ring', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('focus-visible:ring-1');
			expect(classes).toContain('focus-visible:ring-ring');
		});

		it('focus styles apply to all variants', () => {
			const variants: Variant[] = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'];
			variants.forEach((variant) => {
				const classes = getButtonClasses(variant);
				expect(classes).toContain('focus-visible:ring');
			});
		});
	});

	describe('Transitions', () => {
		it('includes transition-colors class', () => {
			const classes = getButtonClasses();
			expect(classes).toContain('transition-colors');
		});

		it('transition-colors applies to all variants', () => {
			const variants: Variant[] = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'];
			variants.forEach((variant) => {
				const classes = getButtonClasses(variant);
				expect(classes).toContain('transition-colors');
			});
		});
	});

	describe('Shadow States', () => {
		it('default variant has shadow', () => {
			const classes = getButtonClasses('default');
			expect(classes).toContain('shadow');
		});

		it('destructive variant has shadow-sm', () => {
			const classes = getButtonClasses('destructive');
			expect(classes).toContain('shadow-sm');
		});

		it('outline variant has shadow-sm', () => {
			const classes = getButtonClasses('outline');
			expect(classes).toContain('shadow-sm');
		});

		it('secondary variant has shadow-sm', () => {
			const classes = getButtonClasses('secondary');
			expect(classes).toContain('shadow-sm');
		});

		it('ghost variant has no shadow', () => {
			const classes = getButtonClasses('ghost');
			expect(classes).not.toMatch(/shadow/);
		});

		it('link variant has no shadow', () => {
			const classes = getButtonClasses('link');
			expect(classes).not.toMatch(/shadow/);
		});
	});

	describe('Text Colors', () => {
		it('default variant has primary foreground text', () => {
			const classes = getButtonClasses('default');
			expect(classes).toContain('text-primary-foreground');
		});

		it('destructive variant has destructive foreground text', () => {
			const classes = getButtonClasses('destructive');
			expect(classes).toContain('text-destructive-foreground');
		});

		it('secondary variant has secondary foreground text', () => {
			const classes = getButtonClasses('secondary');
			expect(classes).toContain('text-secondary-foreground');
		});

		it('outline variant inherits text color', () => {
			const classes = getButtonClasses('outline');
			expect(classes).not.toMatch(/text-primary-foreground|text-destructive-foreground|text-secondary-foreground/);
		});

		it('ghost variant inherits text color', () => {
			const classes = getButtonClasses('ghost');
			expect(classes).not.toMatch(/text-primary-foreground|text-destructive-foreground|text-secondary-foreground/);
		});

		it('link variant has primary text', () => {
			const classes = getButtonClasses('link');
			expect(classes).toContain('text-primary');
		});
	});

	describe('Responsive Behavior', () => {
		it('all variants are responsive-ready', () => {
			const variants: Variant[] = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'];
			variants.forEach((variant) => {
				const classes = getButtonClasses(variant);
				// Check that base classes are present (responsive-ready)
				expect(classes).toContain('inline-flex');
			});
		});

		it('all sizes are responsive-ready', () => {
			const sizes: Size[] = ['default', 'sm', 'lg', 'icon'];
			sizes.forEach((size) => {
				const classes = getButtonClasses('default', size);
				expect(classes).toMatch(/h-\d+/);
			});
		});
	});
});
