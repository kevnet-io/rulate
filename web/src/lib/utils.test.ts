/**
 * Tests for utility functions
 *
 * Tests the cn() utility for merging class names and Tailwind CSS classes.
 */

import { describe, it, expect } from 'vitest';
import { cn } from './utils';

describe('cn utility', () => {
	it('returns empty string when no arguments provided', () => {
		const result = cn();
		expect(result).toBe('');
	});

	it('merges single class name', () => {
		const result = cn('px-2');
		expect(result).toBe('px-2');
	});

	it('merges multiple class names', () => {
		const result = cn('px-2', 'py-4', 'bg-blue-500');
		expect(result).toContain('px-2');
		expect(result).toContain('py-4');
		expect(result).toContain('bg-blue-500');
	});

	it('handles conditional classes with objects', () => {
		const result = cn({
			'bg-red-500': true,
			'bg-blue-500': false,
			'px-2': true
		});
		expect(result).toContain('bg-red-500');
		expect(result).toContain('px-2');
		expect(result).not.toContain('bg-blue-500');
	});

	it('merges conflicting Tailwind classes correctly', () => {
		// When classes conflict, tailwind-merge should keep the last one
		const result = cn('bg-red-500', 'bg-blue-500');
		// Should have only one bg- class (the last one wins)
		expect(result).toContain('bg-blue-500');
		expect(result.split('bg-').length).toBe(2); // "bg-blue-500" and empty string after split
	});

	it('handles array of class names', () => {
		const classes = ['px-2', 'py-4', 'rounded'];
		const result = cn(classes);
		expect(result).toContain('px-2');
		expect(result).toContain('py-4');
		expect(result).toContain('rounded');
	});

	it('handles undefined and null values', () => {
		const result = cn('px-2', undefined, 'py-4', null, 'rounded');
		expect(result).toContain('px-2');
		expect(result).toContain('py-4');
		expect(result).toContain('rounded');
	});

	it('handles false and empty string values', () => {
		const result = cn('px-2', false, '', 'py-4');
		expect(result).toContain('px-2');
		expect(result).toContain('py-4');
	});

	it('combines string and object class specifications', () => {
		const result = cn('px-2', {
			'py-4': true,
			'bg-red-500': false
		}, 'rounded');
		expect(result).toContain('px-2');
		expect(result).toContain('py-4');
		expect(result).toContain('rounded');
		expect(result).not.toContain('bg-red-500');
	});

	it('handles complex Tailwind class combinations', () => {
		const result = cn(
			'flex items-center justify-between',
			'gap-4',
			'p-4 rounded-lg border border-gray-200',
			{
				'shadow-md': true,
				'shadow-lg': false
			}
		);
		expect(result).toContain('flex');
		expect(result).toContain('items-center');
		expect(result).toContain('justify-between');
		expect(result).toContain('gap-4');
		expect(result).toContain('p-4');
		expect(result).toContain('rounded-lg');
		expect(result).toContain('border');
		expect(result).toContain('border-gray-200');
		expect(result).toContain('shadow-md');
		expect(result).not.toContain('shadow-lg');
	});

	it('handles padding class conflicts (last one wins)', () => {
		const result = cn('p-2', 'p-4', 'p-6');
		// Only the last padding class should remain
		expect(result).toContain('p-6');
		expect(result.split('p-').length).toBe(2); // Only one p- class
	});

	it('handles color class conflicts (last one wins)', () => {
		const result = cn('bg-red-500', 'bg-blue-500', 'bg-green-500');
		expect(result).toContain('bg-green-500');
		// Should only have the final bg color
		expect(result.split('bg-').length).toBe(2);
	});

	it('preserves non-conflicting classes', () => {
		const result = cn('flex', 'p-4', 'bg-white', 'rounded', 'shadow');
		expect(result).toContain('flex');
		expect(result).toContain('p-4');
		expect(result).toContain('bg-white');
		expect(result).toContain('rounded');
		expect(result).toContain('shadow');
	});

	it('returns a string type', () => {
		const result = cn('px-2', 'py-4');
		expect(typeof result).toBe('string');
	});
});
