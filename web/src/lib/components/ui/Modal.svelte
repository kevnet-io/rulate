<script lang="ts">
	import { fade, scale } from 'svelte/transition';
	import { onMount } from 'svelte';
	import type { Snippet } from 'svelte';

	interface Props {
		isOpen: boolean;
		onClose: () => void;
		title?: string;
		size?: 'sm' | 'md' | 'lg' | 'xl';
		children?: Snippet;
	}

	let { isOpen = $bindable(false), onClose, title, size = 'md', children }: Props = $props();

	let modalElement = $state<HTMLElement | undefined>(undefined);
	let previouslyFocusedElement = $state<HTMLElement | null>(null);

	const sizeClasses = {
		sm: 'max-w-sm',
		md: 'max-w-md',
		lg: 'max-w-lg',
		xl: 'max-w-xl'
	};

	// Focus trap
	onMount(() => {
		if (isOpen) {
			previouslyFocusedElement = document.activeElement as HTMLElement;
			setTimeout(() => {
				const firstFocusable = modalElement?.querySelector<HTMLElement>(
					'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
				);
				firstFocusable?.focus();
			}, 0);
		}

		return () => {
			if (previouslyFocusedElement) {
				previouslyFocusedElement.focus();
			}
		};
	});

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			onClose();
		}

		// Focus trap
		if (e.key === 'Tab') {
			const focusableElements = modalElement?.querySelectorAll<HTMLElement>(
				'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
			);

			if (!focusableElements || focusableElements.length === 0) return;

			const firstElement = focusableElements[0];
			const lastElement = focusableElements[focusableElements.length - 1];

			if (e.shiftKey && document.activeElement === firstElement) {
				e.preventDefault();
				lastElement.focus();
			} else if (!e.shiftKey && document.activeElement === lastElement) {
				e.preventDefault();
				firstElement.focus();
			}
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onClose();
		}
	}
</script>

{#if isOpen}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 z-50 bg-black/50"
		transition:fade={{ duration: 200 }}
		onclick={handleBackdropClick}
		onkeydown={handleKeydown}
		role="presentation"
	>
		<!-- Modal -->
		<div class="flex min-h-screen items-center justify-center p-4">
			<div
				bind:this={modalElement}
				class="relative w-full {sizeClasses[
					size
				]} rounded-lg bg-white shadow-xl"
				transition:scale={{ duration: 200, start: 0.95 }}
				role="dialog"
				aria-modal="true"
				aria-labelledby={title ? 'modal-title' : undefined}
			>
				<!-- Header -->
				{#if title}
					<div class="flex items-center justify-between border-b border-gray-200 px-6 py-4">
						<h2 id="modal-title" class="text-xl font-semibold text-gray-900">
							{title}
						</h2>
						<button
							onclick={onClose}
							class="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
							aria-label="Close modal"
						>
							<svg
								class="h-5 w-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								aria-hidden="true"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/if}

				<!-- Content -->
				<div class="px-6 py-4">
					{@render children?.()}
				</div>
			</div>
		</div>
	</div>
{/if}
