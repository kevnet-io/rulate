/**
 * Utility to warn users about unsaved changes before navigation
 * Usage in a form component:
 *
 * ```svelte
 * <script>
 *   import { useUnsavedChangesWarning } from '$lib/utils/unsaved-changes.svelte';
 *
 *   let hasUnsavedChanges = $state(false);
 *   useUnsavedChangesWarning(() => hasUnsavedChanges);
 * </script>
 * ```
 */

import { onMount } from 'svelte';
import { beforeNavigate } from '$app/navigation';
import { modalStore } from '$lib/stores/modal.svelte';

export function useUnsavedChangesWarning(hasChanges: () => boolean) {
	// Warn on browser refresh/close
	onMount(() => {
		const handleBeforeUnload = (e: BeforeUnloadEvent) => {
			if (hasChanges()) {
				e.preventDefault();
				e.returnValue = ''; // Chrome requires returnValue to be set
			}
		};

		window.addEventListener('beforeunload', handleBeforeUnload);

		return () => {
			window.removeEventListener('beforeunload', handleBeforeUnload);
		};
	});

	// Warn on SvelteKit navigation
	beforeNavigate(async ({ cancel, to }) => {
		if (hasChanges() && to) {
			const confirmed = await modalStore.confirm({
				title: 'Unsaved Changes',
				message: 'You have unsaved changes. Are you sure you want to leave this page?',
				confirmText: 'Leave Page',
				cancelText: 'Stay',
				isDanger: true
			});

			if (!confirmed) {
				cancel();
			}
		}
	});
}
