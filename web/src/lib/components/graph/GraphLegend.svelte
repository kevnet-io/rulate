<script lang="ts">
  import {
    nodeCategoryColors,
    nodeCategoryLabels,
    edgeCategoryColors,
    edgeCategoryLabels,
    type NodeCategory,
    type EdgeCategory,
  } from "./graph-config";

  // Props
  interface Props {
    showIncompatible?: boolean;
  }

  let { showIncompatible = false }: Props = $props();

  // Determine which node categories to show
  let nodeCategories = $derived<NodeCategory[]>(
    showIncompatible
      ? ["cluster", "valid", "invalid", "incompatible"]
      : ["cluster", "valid", "invalid"],
  );

  // Determine which edge categories to show
  let edgeCategories = $derived<EdgeCategory[]>(
    showIncompatible ? ["compatible", "incompatible"] : ["compatible"],
  );
</script>

<div class="flex flex-col gap-3">
  <!-- Node Categories -->
  <div>
    <h4 class="text-xs font-semibold text-muted-foreground mb-2">Nodes</h4>
    <div class="flex flex-wrap gap-2">
      {#each nodeCategories as category}
        <div class="flex items-center gap-1.5">
          <div
            class="w-3 h-3 rounded-full border border-white/30"
            style="background-color: {nodeCategoryColors[category]};"
            aria-hidden="true"
          ></div>
          <span class="text-xs text-muted-foreground">
            {nodeCategoryLabels[category]}
          </span>
        </div>
      {/each}
    </div>
  </div>

  <!-- Edge Categories -->
  <div>
    <h4 class="text-xs font-semibold text-muted-foreground mb-2">Edges</h4>
    <div class="flex flex-wrap gap-2">
      {#each edgeCategories as category}
        <div class="flex items-center gap-1.5">
          <div
            class="w-6 h-0.5 {category === 'incompatible'
              ? 'border-t-2 border-dashed'
              : ''}"
            style="background-color: {category === 'compatible'
              ? edgeCategoryColors[category]
              : 'transparent'}; border-color: {category === 'incompatible'
              ? edgeCategoryColors[category]
              : 'transparent'};"
            aria-hidden="true"
          ></div>
          <span class="text-xs text-muted-foreground">
            {edgeCategoryLabels[category]}
          </span>
        </div>
      {/each}
    </div>
  </div>
</div>
