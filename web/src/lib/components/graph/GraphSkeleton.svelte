<script lang="ts">
  /**
   * Loading skeleton for graph visualization
   * Displays an animated placeholder while graph data is loading
   */
</script>

<div
  class="w-full h-full min-h-[400px] bg-background border border-border rounded-md p-4 animate-pulse"
  role="status"
  aria-label="Loading graph visualization"
>
  <div class="h-full flex items-center justify-center">
    <!-- Skeleton graph structure -->
    <div class="relative w-full max-w-md h-64">
      <!-- Skeleton nodes -->
      <div
        class="absolute top-1/2 left-1/4 w-12 h-12 bg-gray-300 rounded-full"
      ></div>
      <div
        class="absolute top-1/4 left-1/2 w-12 h-12 bg-gray-300 rounded-full"
      ></div>
      <div
        class="absolute top-3/4 left-1/2 w-12 h-12 bg-gray-300 rounded-full"
      ></div>
      <div
        class="absolute top-1/2 left-3/4 w-12 h-12 bg-gray-300 rounded-full"
      ></div>
      <div
        class="absolute top-1/3 left-1/3 w-12 h-12 bg-gray-300 rounded-full"
      ></div>

      <!-- Skeleton edges (connecting lines) -->
      <svg class="absolute inset-0 w-full h-full" style="z-index: -1;">
        <line
          x1="25%"
          y1="50%"
          x2="50%"
          y2="25%"
          stroke="#d1d5db"
          stroke-width="2"
        />
        <line
          x1="25%"
          y1="50%"
          x2="33%"
          y2="33%"
          stroke="#d1d5db"
          stroke-width="2"
        />
        <line
          x1="50%"
          y1="25%"
          x2="75%"
          y2="50%"
          stroke="#d1d5db"
          stroke-width="2"
        />
        <line
          x1="50%"
          y1="75%"
          x2="75%"
          y2="50%"
          stroke="#d1d5db"
          stroke-width="2"
        />
        <line
          x1="33%"
          y1="33%"
          x2="50%"
          y2="25%"
          stroke="#d1d5db"
          stroke-width="2"
        />
      </svg>
    </div>
  </div>

  <!-- Loading text -->
  <div class="text-center text-sm text-muted-foreground mt-4">
    Loading compatibility graph...
  </div>
</div>
