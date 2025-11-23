<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils.js';

	type $$Props = HTMLAttributes<HTMLHeadingElement>;

	let className: $$Props['class'] = undefined;
	export { className as class };
</script>

<h3 class={cn('font-semibold leading-none tracking-tight text-2xl', className)} {...$$restProps}>
	<slot />
</h3>
