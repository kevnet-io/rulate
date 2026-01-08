<script lang="ts">
  import Button from "$lib/components/ui/button/button.svelte";
  import type { LayoutType } from "./graph-config";

  // Props
  interface Props {
    layout: LayoutType;
    showIncompatible: boolean;
    onLayoutChange: (layout: LayoutType) => void;
    onZoomIn: () => void;
    onZoomOut: () => void;
    onFit: () => void;
    onToggleIncompatible: () => void;
  }

  let {
    layout = $bindable(),
    showIncompatible = $bindable(),
    onLayoutChange,
    onZoomIn,
    onZoomOut,
    onFit,
    onToggleIncompatible,
  }: Props = $props();

  // Layout options
  const layoutOptions: { value: LayoutType; label: string }[] = [
    { value: "force", label: "Force-Directed" },
    { value: "circular", label: "Circular" },
    { value: "grid", label: "Grid" },
    { value: "hierarchical", label: "Hierarchical" },
  ];

  // Handle layout change
  function handleLayoutChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newLayout = target.value as LayoutType;
    onLayoutChange(newLayout);
  }

  // Handle incompatible toggle
  function handleToggleIncompatible() {
    onToggleIncompatible();
  }
</script>

<div class="flex flex-wrap items-center gap-3">
  <!-- Layout Selector -->
  <div class="flex items-center gap-2">
    <label for="layout-select" class="text-sm font-medium">Layout:</label>
    <select
      id="layout-select"
      value={layout}
      onchange={handleLayoutChange}
      class="px-3 py-1.5 text-sm border rounded-md bg-background"
      aria-label="Select graph layout"
    >
      {#each layoutOptions as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>
  </div>

  <!-- Zoom Controls -->
  <div class="flex items-center gap-1">
    <Button
      type="button"
      variant="outline"
      size="sm"
      onclick={onZoomIn}
      aria-label="Zoom in"
      title="Zoom in"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="11" y1="8" x2="11" y2="14"></line>
        <line x1="8" y1="11" x2="14" y2="11"></line>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
    </Button>

    <Button
      type="button"
      variant="outline"
      size="sm"
      onclick={onZoomOut}
      aria-label="Zoom out"
      title="Zoom out"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="8" y1="11" x2="14" y2="11"></line>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
    </Button>

    <Button
      type="button"
      variant="outline"
      size="sm"
      onclick={onFit}
      aria-label="Fit to screen"
      title="Fit to screen"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M8 3H5a2 2 0 0 0-2 2v3"></path>
        <path d="M21 8V5a2 2 0 0 0-2-2h-3"></path>
        <path d="M3 16v3a2 2 0 0 0 2 2h3"></path>
        <path d="M16 21h3a2 2 0 0 0 2-2v-3"></path>
      </svg>
    </Button>
  </div>

  <!-- Show Incompatible Toggle -->
  <div class="flex items-center gap-2">
    <input
      id="show-incompatible"
      type="checkbox"
      checked={showIncompatible}
      onchange={handleToggleIncompatible}
      class="w-4 h-4 rounded border-gray-300"
      aria-label="Show incompatible items"
    />
    <label for="show-incompatible" class="text-sm"> Show Incompatible </label>
  </div>
</div>
