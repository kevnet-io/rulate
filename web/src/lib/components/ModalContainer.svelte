<script lang="ts">
	import { modalStore } from '$lib/stores/modal.svelte';
	import ConfirmModal from './ui/ConfirmModal.svelte';
</script>

{#if modalStore.isOpen && modalStore.data}
	<ConfirmModal
		bind:isOpen={modalStore.isOpen}
		onClose={modalStore.handleCancel}
		onConfirm={modalStore.handleConfirm}
		title={modalStore.data.title}
		message={modalStore.data.message}
		confirmText={modalStore.data.confirmText}
		cancelText={modalStore.data.cancelText}
		isDanger={modalStore.data.isDanger}
	/>
{/if}
