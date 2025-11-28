/**
 * Test setup for Vitest
 *
 * This file is automatically loaded before tests run.
 */

import '@testing-library/jest-dom';
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/svelte';

// Cleanup after each test
afterEach(() => {
	cleanup();
});
