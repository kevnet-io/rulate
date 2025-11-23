<script lang="ts">
	import '../app.css';
	import Navigation from '$lib/components/Navigation.svelte';
</script>

<div class="min-h-screen flex flex-col">
	<Navigation />
	<main class="flex-1">
		<slot />
	</main>
</div>
