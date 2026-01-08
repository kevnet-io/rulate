<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api/client";
  import type {
    Catalog,
    RuleSet,
    ClusterRuleSet,
    Item,
    EvaluateCandidatesResponse,
    EvaluationMatrix,
  } from "$lib/api/client";
  import Card from "$lib/components/ui/card/card.svelte";
  import CardHeader from "$lib/components/ui/card/card-header.svelte";
  import CardTitle from "$lib/components/ui/card/card-title.svelte";
  import CardDescription from "$lib/components/ui/card/card-description.svelte";
  import CardContent from "$lib/components/ui/card/card-content.svelte";
  import Button from "$lib/components/ui/button/button.svelte";
  import Badge from "$lib/components/ui/badge/badge.svelte";
  import { toastStore } from "$lib/stores/toast.svelte";
  import {
    clusterItemClass,
    validCandidateClass,
    invalidCandidateClass,
    incompatibleItemClass,
  } from "./styles";
  import CompatibilityGraph from "$lib/components/graph/CompatibilityGraph.svelte";
  import GraphControls from "$lib/components/graph/GraphControls.svelte";
  import GraphLegend from "$lib/components/graph/GraphLegend.svelte";
  import { transformToGraphData } from "$lib/components/graph/graph-utils";
  import type { LayoutType } from "$lib/components/graph/graph-config";

  // Configuration state
  let catalogs = $state<Catalog[]>([]);
  let rulesets = $state<RuleSet[]>([]);
  let clusterRulesets = $state<ClusterRuleSet[]>([]);
  let items = $state<Item[]>([]);

  let selectedCatalog = $state("");
  let selectedRuleset = $state("");
  let selectedClusterRuleset = $state("");

  // Cluster state
  let clusterItemIds = $state<string[]>([]);
  let candidatesResponse = $state<EvaluateCandidatesResponse | null>(null);

  // UI state
  let loading = $state(false);
  let error = $state<string | null>(null);
  let showIncompatible = $state(false);

  // Graph state
  let graphExpanded = $state(false);
  let graphLayout = $state<LayoutType>("force");
  let showIncompatibleEdges = $state(false);
  let matrixData = $state<EvaluationMatrix | null>(null);
  let loadingGraph = $state(false);
  let graphComponentRef = $state<CompatibilityGraph | null>(null);

  // Computed values
  let clusterItems = $derived(
    clusterItemIds
      .map((id) => items.find((i) => i.item_id === id))
      .filter((i): i is Item => i !== undefined),
  );

  let compatibleCandidates = $derived(
    candidatesResponse?.candidates.filter((c) => c.is_pairwise_compatible) ??
      [],
  );

  let incompatibleCandidates = $derived(
    candidatesResponse?.candidates.filter((c) => !c.is_pairwise_compatible) ??
      [],
  );

  let graphData = $derived(
    transformToGraphData(
      items,
      matrixData,
      clusterItemIds,
      candidatesResponse?.candidates ?? null,
      showIncompatibleEdges,
    ),
  );

  async function loadOptions() {
    try {
      const [catalogsData, rulesetsData, clusterRulesetsData] =
        await Promise.all([
          api.getCatalogs(),
          api.getRuleSets(),
          api.getClusterRuleSets(),
        ]);
      catalogs = catalogsData;
      rulesets = rulesetsData;
      clusterRulesets = clusterRulesetsData;

      if (catalogs.length > 0) {
        selectedCatalog = catalogs[0].name;
      }
      if (rulesets.length > 0) {
        selectedRuleset = rulesets[0].name;
      }
      if (clusterRulesets.length > 0) {
        selectedClusterRuleset = clusterRulesets[0].name;
      }
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load options";
      toastStore.error(error);
    }
  }

  async function loadItems() {
    if (!selectedCatalog) return;
    try {
      items = await api.getItems(selectedCatalog);
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load items";
      toastStore.error(error);
    }
  }

  async function evaluateCandidates() {
    if (!selectedCatalog || !selectedRuleset || !selectedClusterRuleset) {
      return;
    }

    try {
      loading = true;
      error = null;

      candidatesResponse = await api.evaluateCandidates(
        selectedCatalog,
        selectedRuleset,
        selectedClusterRuleset,
        clusterItemIds,
      );
    } catch (err) {
      error =
        err instanceof Error ? err.message : "Failed to evaluate candidates";
      toastStore.error(error);
    } finally {
      loading = false;
    }
  }

  function addItem(itemId: string) {
    if (!clusterItemIds.includes(itemId)) {
      clusterItemIds = [...clusterItemIds, itemId];
    }
  }

  function removeItem(itemId: string) {
    clusterItemIds = clusterItemIds.filter((id) => id !== itemId);
  }

  function clearCluster() {
    clusterItemIds = [];
  }

  // Graph functions
  async function fetchGraphData() {
    if (!selectedCatalog || !selectedRuleset) {
      return;
    }

    try {
      loadingGraph = true;
      matrixData = await api.evaluateMatrix(selectedCatalog, selectedRuleset);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load graph data";
      toastStore.error(message);
    } finally {
      loadingGraph = false;
    }
  }

  function handleNodeClick(nodeId: string) {
    if (clusterItemIds.includes(nodeId)) {
      removeItem(nodeId);
    } else {
      addItem(nodeId);
    }
  }

  function handleLayoutChange(newLayout: LayoutType) {
    graphLayout = newLayout;
  }

  function toggleIncompatibleEdges() {
    showIncompatibleEdges = !showIncompatibleEdges;
  }

  function handleZoomIn() {
    graphComponentRef?.zoomIn();
  }

  function handleZoomOut() {
    graphComponentRef?.zoomOut();
  }

  function handleFit() {
    graphComponentRef?.fit();
  }

  function toggleGraphExpanded() {
    graphExpanded = !graphExpanded;
    if (graphExpanded && !matrixData) {
      fetchGraphData();
    }
  }

  // Re-evaluate when cluster changes
  $effect(() => {
    if (selectedCatalog && selectedRuleset && selectedClusterRuleset) {
      evaluateCandidates();
    }
  });

  // Load items when catalog changes
  $effect(() => {
    if (selectedCatalog) {
      loadItems();
      clusterItemIds = [];
      candidatesResponse = null;
    }
  });

  // Clear graph data when catalog or ruleset changes
  $effect(() => {
    if (selectedCatalog || selectedRuleset) {
      matrixData = null;
      graphExpanded = false;
    }
  });

  onMount(loadOptions);
</script>

<svelte:head>
  <title>Cluster Builder - Rulate</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold mb-2">Cluster Builder</h1>
    <p class="text-muted-foreground">
      Build clusters interactively - add items and see real-time validation
      feedback
    </p>
  </div>

  <div class="space-y-6">
    <!-- Configuration -->
    <Card>
      <CardHeader>
        <CardTitle>Configuration</CardTitle>
        <CardDescription>
          Select catalog and rulesets to start building
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="grid gap-4 md:grid-cols-3">
          <div>
            <label for="catalog" class="block text-sm font-medium mb-2">
              Catalog
            </label>
            <select
              id="catalog"
              bind:value={selectedCatalog}
              class="w-full px-3 py-2 border rounded-md bg-background"
            >
              {#each catalogs as catalog}
                <option value={catalog.name}>{catalog.name}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="ruleset" class="block text-sm font-medium mb-2">
              Pairwise RuleSet
            </label>
            <select
              id="ruleset"
              bind:value={selectedRuleset}
              class="w-full px-3 py-2 border rounded-md bg-background"
            >
              {#each rulesets as ruleset}
                <option value={ruleset.name}>{ruleset.name}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="cluster-ruleset" class="block text-sm font-medium mb-2">
              Cluster RuleSet
            </label>
            <select
              id="cluster-ruleset"
              bind:value={selectedClusterRuleset}
              class="w-full px-3 py-2 border rounded-md bg-background"
            >
              {#each clusterRulesets as clusterRuleset}
                <option value={clusterRuleset.name}
                  >{clusterRuleset.name}</option
                >
              {/each}
            </select>
          </div>
        </div>

        {#if error}
          <div
            class="mt-4 p-3 bg-destructive/10 border border-destructive rounded-md"
          >
            <p class="text-sm text-destructive">{error}</p>
          </div>
        {/if}
      </CardContent>
    </Card>

    <!-- Current Cluster -->
    <Card
      class={candidatesResponse?.base_validation.is_valid
        ? "border-2 border-emerald-500"
        : clusterItemIds.length > 0
          ? "border-2 border-amber-500"
          : ""}
    >
      <CardHeader>
        <div class="flex items-start justify-between">
          <div>
            <CardTitle>
              Current Cluster ({clusterItemIds.length} items)
            </CardTitle>
            <CardDescription>
              {#if clusterItemIds.length === 0}
                Click on items below to start building your cluster
              {:else}
                Click items to remove them from the cluster
              {/if}
            </CardDescription>
          </div>
          <div class="flex items-center gap-2">
            {#if candidatesResponse?.base_validation}
              {#if candidatesResponse.base_validation.is_valid}
                <Badge variant="default" class="bg-emerald-600">
                  ✓ Valid Cluster
                </Badge>
              {:else}
                <Badge variant="secondary" class="bg-amber-600 text-white">
                  ⚠ Invalid
                </Badge>
              {/if}
            {/if}
            {#if clusterItemIds.length > 0}
              <Button variant="outline" size="sm" onclick={clearCluster}>
                Clear
              </Button>
            {/if}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {#if clusterItemIds.length === 0}
          <p class="text-muted-foreground text-sm italic">
            No items in cluster yet. Select items from the list below.
          </p>
        {:else}
          <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {#each clusterItems as item}
              <button
                onclick={() => removeItem(item.item_id)}
                class={clusterItemClass}
              >
                <div class="flex items-start justify-between">
                  <div class="min-w-0 flex-1">
                    <h4 class="font-semibold text-sm truncate">{item.name}</h4>
                    <p class="text-xs text-muted-foreground truncate">
                      {item.item_id}
                    </p>
                  </div>
                  <span class="text-muted-foreground text-xs ml-2">✕</span>
                </div>
              </button>
            {/each}
          </div>

          <!-- Rule Evaluations -->
          {#if candidatesResponse?.base_validation.rule_evaluations}
            <div class="mt-4 pt-4 border-t">
              <div class="text-sm font-medium mb-2">Cluster Rules:</div>
              <div class="flex flex-wrap gap-2">
                {#each candidatesResponse.base_validation.rule_evaluations as rule}
                  <Badge
                    variant={rule.passed ? "outline" : "destructive"}
                    class="text-xs"
                  >
                    {rule.passed ? "✓" : "✗"}
                    {rule.rule_name}
                  </Badge>
                {/each}
              </div>
            </div>
          {/if}
        {/if}
      </CardContent>
    </Card>

    <!-- Compatibility Graph -->
    <Card>
      <CardHeader>
        <button
          type="button"
          onclick={toggleGraphExpanded}
          class="w-full flex items-center justify-between text-left"
        >
          <div>
            <CardTitle>
              {graphExpanded ? "▼" : "▸"} Compatibility Graph
            </CardTitle>
            <CardDescription>
              Visual network showing pairwise compatibility between items
            </CardDescription>
          </div>
        </button>
      </CardHeader>

      {#if graphExpanded}
        <CardContent>
          <!-- Loading State -->
          {#if loadingGraph}
            <div class="py-8 text-center text-muted-foreground">
              <div class="animate-pulse">Loading graph data...</div>
            </div>

            <!-- Graph Controls and Visualization -->
          {:else if matrixData}
            <div class="space-y-4">
              <!-- Controls -->
              <div class="flex flex-wrap items-center justify-between gap-4">
                <GraphControls
                  layout={graphLayout}
                  showIncompatible={showIncompatibleEdges}
                  onLayoutChange={handleLayoutChange}
                  onZoomIn={handleZoomIn}
                  onZoomOut={handleZoomOut}
                  onFit={handleFit}
                  onToggleIncompatible={toggleIncompatibleEdges}
                />
              </div>

              <!-- Graph Container -->
              <div class="border rounded-md" style="height: 500px;">
                <CompatibilityGraph
                  bind:this={graphComponentRef}
                  nodes={graphData.nodes}
                  edges={graphData.edges}
                  layout={graphLayout}
                  onNodeClick={handleNodeClick}
                />
              </div>

              <!-- Legend -->
              <GraphLegend showIncompatible={showIncompatibleEdges} />

              <!-- Help Text -->
              <div class="text-sm text-muted-foreground italic">
                Click nodes to add/remove items from cluster. Compatible pairs
                are connected with solid green lines.
                {#if showIncompatibleEdges}
                  Incompatible pairs shown with dashed red lines.
                {/if}
              </div>
            </div>

            <!-- Error or Empty State -->
          {:else}
            <div class="py-8 text-center text-muted-foreground">
              No graph data available. Select a catalog and ruleset to view
              compatibility graph.
            </div>
          {/if}
        </CardContent>
      {/if}
    </Card>

    <!-- Compatible Items -->
    {#if loading}
      <Card>
        <CardContent class="py-8">
          <div class="text-center text-muted-foreground">
            <div class="animate-pulse">Evaluating candidates...</div>
          </div>
        </CardContent>
      </Card>
    {:else if compatibleCandidates.length > 0 || clusterItemIds.length === 0}
      <Card>
        <CardHeader>
          <CardTitle>
            Available Items ({compatibleCandidates.length} compatible)
          </CardTitle>
          <CardDescription>
            Items compatible with all current cluster items. Click to add.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {#if compatibleCandidates.length === 0 && items.length > 0}
            <p class="text-muted-foreground text-sm italic">
              Select items from the catalog to start building your cluster.
            </p>
            <div
              class="grid gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 mt-4"
            >
              {#each items.filter((i) => !clusterItemIds.includes(i.item_id)) as item}
                <button
                  onclick={() => addItem(item.item_id)}
                  class={validCandidateClass}
                >
                  <div class="flex items-start justify-between mb-2">
                    <div class="min-w-0 flex-1">
                      <h4 class="font-semibold text-sm truncate">
                        {item.name}
                      </h4>
                      <p class="text-xs text-muted-foreground truncate">
                        {item.item_id}
                      </p>
                    </div>
                    <span class="text-emerald-600 text-sm">+</span>
                  </div>
                </button>
              {/each}
            </div>
          {:else}
            <div
              class="grid gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
            >
              {#each compatibleCandidates as candidate}
                {@const item = items.find(
                  (i) => i.item_id === candidate.item_id,
                )}
                {@const wouldBeValid = candidate.cluster_if_added.is_valid}
                {@const failedRules =
                  candidate.cluster_if_added.rule_evaluations.filter(
                    (r) => !r.passed,
                  )}
                {#if item}
                  <button
                    onclick={() => addItem(candidate.item_id)}
                    class={wouldBeValid
                      ? validCandidateClass
                      : invalidCandidateClass}
                  >
                    <div class="flex items-start justify-between mb-2">
                      <div class="min-w-0 flex-1">
                        <h4 class="font-semibold text-sm truncate">
                          {item.name}
                        </h4>
                        <p class="text-xs text-muted-foreground truncate">
                          {item.item_id}
                        </p>
                      </div>
                      {#if wouldBeValid}
                        <Badge variant="default" class="text-xs bg-emerald-600">
                          ✓ Valid
                        </Badge>
                      {:else}
                        <Badge
                          variant="secondary"
                          class="text-xs bg-amber-600 text-white"
                        >
                          ⚠
                        </Badge>
                      {/if}
                    </div>
                    {#if !wouldBeValid && failedRules.length > 0}
                      <div class="text-xs text-amber-700 dark:text-amber-400">
                        Would break: {failedRules
                          .map((r) => r.rule_name)
                          .join(", ")}
                      </div>
                    {:else if wouldBeValid}
                      <div
                        class="text-xs text-emerald-700 dark:text-emerald-400"
                      >
                        Would form valid cluster
                      </div>
                    {/if}
                  </button>
                {/if}
              {/each}
            </div>
          {/if}
        </CardContent>
      </Card>
    {/if}

    <!-- Incompatible Items (collapsible) -->
    {#if incompatibleCandidates.length > 0}
      <Card>
        <CardHeader>
          <button
            onclick={() => (showIncompatible = !showIncompatible)}
            class="flex items-center justify-between w-full text-left"
          >
            <div>
              <CardTitle>
                Incompatible Items ({incompatibleCandidates.length})
              </CardTitle>
              <CardDescription>
                Items that conflict with current cluster items (pairwise rules)
              </CardDescription>
            </div>
            <span class="text-muted-foreground text-lg">
              {showIncompatible ? "▼" : "▸"}
            </span>
          </button>
        </CardHeader>
        {#if showIncompatible}
          <CardContent>
            <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
              {#each incompatibleCandidates as candidate}
                {@const item = items.find(
                  (i) => i.item_id === candidate.item_id,
                )}
                {#if item}
                  <div class={incompatibleItemClass}>
                    <div class="flex items-start justify-between">
                      <div class="min-w-0 flex-1">
                        <h4 class="font-medium text-xs truncate">
                          {item.name}
                        </h4>
                        <p class="text-xs text-muted-foreground truncate">
                          {item.item_id}
                        </p>
                      </div>
                      <Badge variant="destructive" class="text-xs">✗</Badge>
                    </div>
                    <div class="mt-2 text-xs text-rose-600 dark:text-rose-400">
                      Pairwise conflict
                    </div>
                  </div>
                {/if}
              {/each}
            </div>
          </CardContent>
        {/if}
      </Card>
    {/if}
  </div>
</div>
