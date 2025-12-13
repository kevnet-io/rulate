<script lang="ts">
	import { fade, fly } from 'svelte/transition';
	import type { ToastType } from '$lib/stores/toast.svelte';

	interface Props {
		message: string;
		type?: ToastType;
		onClose: () => void;
	}

	let { message, type = 'info', onClose }: Props = $props();

	const icons = {
		success: '✓',
		error: '✗',
		warning: '⚠',
		info: 'ℹ'
	};

	const colors = {
		success: 'bg-green-500 text-white',
		error: 'bg-red-500 text-white',
		warning: 'bg-yellow-500 text-gray-900',
		info: 'bg-blue-500 text-white'
	};
</script>

<div
	class="flex items-center gap-3 rounded-lg px-4 py-3 shadow-lg {colors[type]} min-w-[300px] max-w-md"
	transition:fly={{ x: 300, duration: 300 }}
	role="alert"
	aria-live="polite"
>
	<div class="flex-shrink-0 text-xl font-bold" aria-hidden="true">
		{icons[type]}
	</div>
	<div class="flex-1 text-sm font-medium">
		{message}
	</div>
	<button
		onclick={onClose}
		class="flex-shrink-0 rounded p-1 hover:bg-black/10 focus:outline-none focus:ring-2 focus:ring-white/50"
		aria-label="Close notification"
	>
		<svg
			class="h-4 w-4"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
			aria-hidden="true"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
		</svg>
	</button>
</div>
