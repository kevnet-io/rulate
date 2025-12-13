<script lang="ts">
	import '../app.css';
	import Navigation from '$lib/components/Navigation.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';
	import ModalContainer from '$lib/components/ModalContainer.svelte';
</script>

<div class="min-h-screen flex flex-col">
	<Navigation />
	<main class="flex-1">
		<slot />
	</main>
	<ToastContainer />
	<ModalContainer />
</div>
