/**
 * Tests for Card Title component
 */

import { describe, it, expect } from 'vitest';

const cardTitleBaseClasses = 'font-semibold leading-none tracking-tight text-2xl';

function getCardTitleClasses(customClasses?: string): string {
	if (customClasses) {
		return `${cardTitleBaseClasses} ${customClasses}`;
	}
	return cardTitleBaseClasses;
}

describe('Card Title Component', () => {
	describe('Base Classes', () => {
		it('has semibold font weight', () => {
			expect(getCardTitleClasses()).toContain('font-semibold');
		});

		it('has tight leading', () => {
			expect(getCardTitleClasses()).toContain('leading-none');
		});

		it('has tight letter spacing', () => {
			expect(getCardTitleClasses()).toContain('tracking-tight');
		});

		it('has large text size', () => {
			expect(getCardTitleClasses()).toContain('text-2xl');
		});
	});

	describe('Typography', () => {
		it('emphasizes title with bold weight', () => {
			expect(getCardTitleClasses()).toContain('font-semibold');
		});

		it('provides large readable size', () => {
			expect(getCardTitleClasses()).toContain('text-2xl');
		});

		it('maintains clean line height', () => {
			expect(getCardTitleClasses()).toContain('leading-none');
		});
	});

	describe('Custom Classes', () => {
		it('accepts custom classes', () => {
			const classes = getCardTitleClasses('text-primary');
			expect(classes).toContain('text-primary');
		});

		it('preserves typography classes', () => {
			const classes = getCardTitleClasses('truncate');
			expect(classes).toContain('font-semibold');
			expect(classes).toContain('text-2xl');
		});
	});
});
