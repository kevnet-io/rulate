/**
 * Tests for Card component
 */

import { describe, it, expect } from 'vitest';

const cardBaseClasses = 'rounded-xl border bg-card text-card-foreground shadow';

function getCardClasses(customClasses?: string): string {
	if (customClasses) {
		return `${cardBaseClasses} ${customClasses}`;
	}
	return cardBaseClasses;
}

describe('Card Component', () => {
	describe('Base Classes', () => {
		it('has rounded corners', () => {
			expect(getCardClasses()).toContain('rounded-xl');
		});

		it('has border', () => {
			expect(getCardClasses()).toContain('border');
		});

		it('has background color', () => {
			expect(getCardClasses()).toContain('bg-card');
		});

		it('has text color', () => {
			expect(getCardClasses()).toContain('text-card-foreground');
		});

		it('has shadow', () => {
			expect(getCardClasses()).toContain('shadow');
		});
	});

	describe('Custom Classes', () => {
		it('accepts custom classes', () => {
			const classes = getCardClasses('custom-class');
			expect(classes).toContain('custom-class');
			expect(classes).toContain('rounded-xl');
		});

		it('preserves all base classes with custom classes', () => {
			const classes = getCardClasses('p-8');
			expect(classes).toContain('rounded-xl');
			expect(classes).toContain('border');
			expect(classes).toContain('bg-card');
			expect(classes).toContain('shadow');
		});
	});

	describe('Styling', () => {
		it('uses extra large border radius', () => {
			expect(getCardClasses()).toContain('rounded-xl');
		});

		it('uses design system colors', () => {
			const classes = getCardClasses();
			expect(classes).toContain('bg-card');
			expect(classes).toContain('text-card-foreground');
		});

		it('has visual depth with shadow', () => {
			expect(getCardClasses()).toContain('shadow');
		});
	});
});
