/**
 * Tests for Button component
 *
 * Tests cover rendering, variants, sizes, and polymorphic behavior.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Button from './button.svelte';

describe('Button Component', () => {
	describe('Rendering', () => {
		it('renders with default props', () => {
			render(Button, { props: {} });
			const button = screen.getByRole('button');
			expect(button).toBeInTheDocument();
			expect(button).toHaveAttribute('type', 'button');
		});

		it('renders with slot content', () => {
			const { container } = render(Button, {
				props: {},
				context: new Map([['$$slots', { default: true }]]),
			});
			const button = container.querySelector('button');
			expect(button).toBeInTheDocument();
		});

		it('renders as link when href is provided', () => {
			render(Button, {
				props: {
					href: '/test-link'
				}
			});
			const link = screen.getByRole('link');
			expect(link).toBeInTheDocument();
			expect(link).toHaveAttribute('href', '/test-link');
		});
	});

	describe('Type attribute', () => {
		it('defaults to type="button"', () => {
			render(Button, { props: {} });
			const button = screen.getByRole('button');
			expect(button).toHaveAttribute('type', 'button');
		});

		it('accepts type="submit"', () => {
			render(Button, {
				props: {
					type: 'submit'
				}
			});
			const button = screen.getByRole('button');
			expect(button).toHaveAttribute('type', 'submit');
		});

		it('accepts type="reset"', () => {
			render(Button, {
				props: {
					type: 'reset'
				}
			});
			const button = screen.getByRole('button');
			expect(button).toHaveAttribute('type', 'reset');
		});
	});

	describe('Variants', () => {
		it('applies default variant classes', () => {
			render(Button, {
				props: {
					variant: 'default'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('bg-primary');
		});

		it('applies destructive variant classes', () => {
			render(Button, {
				props: {
					variant: 'destructive'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('bg-destructive');
		});

		it('applies outline variant classes', () => {
			render(Button, {
				props: {
					variant: 'outline'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('border');
		});

		it('applies secondary variant classes', () => {
			render(Button, {
				props: {
					variant: 'secondary'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('bg-secondary');
		});

		it('applies ghost variant classes', () => {
			render(Button, {
				props: {
					variant: 'ghost'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('hover:bg-accent');
		});

		it('applies link variant classes', () => {
			render(Button, {
				props: {
					variant: 'link'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('underline');
		});
	});

	describe('Sizes', () => {
		it('applies default size classes', () => {
			render(Button, {
				props: {
					size: 'default'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('h-9');
			expect(button.className).toContain('px-4');
		});

		it('applies small size classes', () => {
			render(Button, {
				props: {
					size: 'sm'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('h-8');
			expect(button.className).toContain('px-3');
		});

		it('applies large size classes', () => {
			render(Button, {
				props: {
					size: 'lg'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('h-10');
			expect(button.className).toContain('px-8');
		});

		it('applies icon size classes', () => {
			render(Button, {
				props: {
					size: 'icon'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('h-9');
			expect(button.className).toContain('w-9');
		});
	});

	describe('Custom classes', () => {
		it('accepts custom class prop', () => {
			render(Button, {
				props: {
					class: 'custom-class'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('custom-class');
		});

		it('merges custom class with variant classes', () => {
			render(Button, {
				props: {
					variant: 'default',
					class: 'custom-class'
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('custom-class');
			expect(button.className).toContain('bg-primary');
		});
	});

	describe('Disabled state', () => {
		it('accepts disabled attribute', () => {
			render(Button, {
				props: {
					disabled: true
				}
			});
			const button = screen.getByRole('button');
			expect(button).toBeDisabled();
		});

		it('applies disabled opacity classes', () => {
			render(Button, {
				props: {
					disabled: true
				}
			});
			const button = screen.getByRole('button');
			expect(button.className).toContain('disabled:opacity-50');
		});
	});

	describe('Additional props', () => {
		it('passes through aria attributes', () => {
			render(Button, {
				props: {
					'aria-label': 'Test button'
				}
			});
			const button = screen.getByRole('button');
			expect(button).toHaveAttribute('aria-label', 'Test button');
		});

		it('passes through data attributes', () => {
			render(Button, {
				props: {
					'data-testid': 'test-button'
				}
			});
			const button = screen.getByRole('button');
			expect(button).toHaveAttribute('data-testid', 'test-button');
		});
	});
});
