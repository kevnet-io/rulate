<script lang="ts">
	import { cn } from '$lib/utils';
	import Tooltip from './Tooltip.svelte';

	interface Props {
		label: string;
		name: string;
		error?: string;
		hint?: string;
		required?: boolean;
		class?: string;
		children?: any;
	}

	let { label, name, error, hint, required = false, class: className, children }: Props = $props();

	const inputId = $derived(`field-${name}`);
	const errorId = $derived(`error-${name}`);
	const hintId = $derived(`hint-${name}`);
</script>

<div class={cn('space-y-2', className)}>
	<label for={inputId} class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-2">
		{label}
		{#if required}
			<span class="text-destructive" aria-label="required">*</span>
		{/if}
		{#if hint}
			<Tooltip text={hint} position="right">
				<span class="text-muted-foreground cursor-help">ℹ</span>
			</Tooltip>
		{/if}
	</label>

	<div>
		{@render children?.({ id: inputId, ariaDescribedBy: error ? errorId : hint ? hintId : undefined })}
	</div>

	{#if error}
		<p id={errorId} class="text-sm text-destructive" role="alert">
			{error}
		</p>
	{/if}
</div>
