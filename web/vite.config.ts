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
		// Use happy-dom for better Svelte 5 compatibility
		environment: 'happy-dom',
		// Ensure Svelte components are transformed for the browser, not SSR, during Vitest runs
		transformMode: {
			web: [/\.svelte$/]
		},
		setupFiles: ['./src/test-setup.ts'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'html', 'json-summary'],
			include: ['src/**/*.{ts,svelte}'],
			exclude: [
				'src/**/*.test.ts',
				'src/**/*.spec.ts',
				'src/test-setup.ts',
				'src/routes/+layout.svelte'
			],
			thresholds: {
				statements: 70,
				branches: 70,
				functions: 70,
				lines: 70
			}
		}
	}
});
