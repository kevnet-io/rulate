import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	resolve: {
		alias: {
			$app: '@sveltejs/kit/src/runtime/app'
		}
	},
	optimizeDeps: {
		exclude: ['@sveltejs/kit']
	},
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true
			}
		}
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		globals: true,
		// Use a real DOM implementation so Svelte components render with client lifecycle APIs
		environment: 'jsdom',
		// Ensure Svelte components are transformed for the browser, not SSR, during Vitest runs
		transformMode: {
			web: [/\.svelte$/]
		},
		setupFiles: ['./src/test-setup.ts']
	}
});
