<script lang="ts">
  import { fade } from "svelte/transition";
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface Props {
    text: string;
    position?: "top" | "bottom" | "left" | "right";
    class?: string;
    children?: Snippet;
  }

  let { text, position = "top", class: className, children }: Props = $props();

  let showTooltip = $state(false);

  const positions = {
    top: "bottom-full right-0 mb-2",
    bottom: "top-full right-0 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  };

  const arrows = {
    top: "top-full right-3 border-l-transparent border-r-transparent border-b-transparent",
    bottom:
      "bottom-full right-3 border-l-transparent border-r-transparent border-t-transparent",
    left: "left-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent",
    right:
      "right-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent",
  };
</script>

<div class={cn("relative inline-block", className)}>
  <div
    onmouseenter={() => (showTooltip = true)}
    onmouseleave={() => (showTooltip = false)}
    onfocus={() => (showTooltip = true)}
    onblur={() => (showTooltip = false)}
    role="button"
    tabindex="0"
  >
    {@render children?.()}
  </div>

  {#if showTooltip}
    <div
      class={cn(
        "absolute z-50 whitespace-nowrap rounded-md bg-gray-900 px-3 py-2 text-xs text-white shadow-lg",
        positions[position],
      )}
      transition:fade={{ duration: 150 }}
      role="tooltip"
    >
      {text}
      <div
        class={cn(
          "absolute h-0 w-0 border-4 border-gray-900",
          arrows[position],
        )}
        aria-hidden="true"
      ></div>
    </div>
  {/if}
</div>
