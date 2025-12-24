<script lang="ts">
  import { cn } from "$lib/utils";

  interface Props {
    size?: "sm" | "md" | "lg";
    class?: string;
    text?: string;
  }

  let { size = "md", class: className, text }: Props = $props();

  const sizes = {
    sm: "h-4 w-4 border-2",
    md: "h-8 w-8 border-2",
    lg: "h-12 w-12 border-3",
  };
</script>

<div class={cn("flex flex-col items-center justify-center gap-3", className)}>
  <div
    class={cn(
      "animate-spin rounded-full border-primary border-t-transparent",
      sizes[size],
    )}
    role="status"
    aria-label="Loading"
  ></div>
  {#if text}
    <p class="text-sm text-muted-foreground">{text}</p>
  {/if}
</div>
