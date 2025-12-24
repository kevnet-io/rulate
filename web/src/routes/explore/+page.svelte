<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api/client";
  import type {
    Catalog,
    RuleSet,
    Item,
    ComparisonResult,
  } from "$lib/api/client";
  import Card from "$lib/components/ui/card/card.svelte";
  import CardHeader from "$lib/components/ui/card/card-header.svelte";
  import CardTitle from "$lib/components/ui/card/card-title.svelte";
  import CardDescription from "$lib/components/ui/card/card-description.svelte";
  import CardContent from "$lib/components/ui/card/card-content.svelte";
  import Button from "$lib/components/ui/button/button.svelte";
  import Badge from "$lib/components/ui/badge/badge.svelte";
  import {
    compatibleItemButtonClass,
    incompatibleItemButtonClass,
  } from "./styles";

  let catalogs = $state<Catalog[]>([]);
  let rulesets = $state<RuleSet[]>([]);
  let items = $state<Item[]>([]);
  let selectedCatalog = $state("");
  let selectedRuleset = $state("");
  let selectedItemId = $state("");
  let loading = $state(false);
  let error = $state<string | null>(null);

  let currentItem = $state<Item | null>(null);
  let compatibleResults = $state<ComparisonResult[]>([]);
  let incompatibleResults = $state<ComparisonResult[]>([]);

  async function loadOptions() {
    try {
      const [catalogsData, rulesetsData] = await Promise.all([
        api.getCatalogs(),
        api.getRuleSets(),
      ]);
      catalogs = catalogsData;
      rulesets = rulesetsData;

      if (catalogs.length > 0) {
        selectedCatalog = catalogs[0].name;
        await loadItems();
      }
      if (rulesets.length > 0) selectedRuleset = rulesets[0].name;
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load options";
    }
  }

  async function loadItems() {
    if (!selectedCatalog) return;
    try {
      items = await api.getItems(selectedCatalog);
      if (items.length > 0 && !selectedItemId) {
        selectedItemId = items[0].item_id;
      }
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load items";
    }
  }

  async function exploreItem(itemId: string) {
    if (!selectedCatalog || !selectedRuleset || !itemId) {
      error = "Please select a catalog, ruleset, and item";
      return;
    }

    try {
      loading = true;
      error = null;

      // Get the item details
      currentItem = items.find((i) => i.item_id === itemId) || null;

      // Evaluate against catalog
      const results = await api.evaluateItem(
        itemId,
        selectedCatalog,
        selectedRuleset,
      );

      // Split into compatible and incompatible
      compatibleResults = results.filter((r) => r.compatible);
      incompatibleResults = results.filter((r) => r.compatible === false);
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to evaluate item";
    } finally {
      loading = false;
    }
  }

  function selectItem(itemId: string) {
    selectedItemId = itemId;
    exploreItem(itemId);
  }

  function getOtherItemId(result: ComparisonResult): string {
    return result.item1_id === currentItem?.item_id
      ? result.item2_id
      : result.item1_id;
  }

  function reset() {
    currentItem = null;
    compatibleResults = [];
    incompatibleResults = [];
  }

  $effect(() => {
    if (selectedCatalog) {
      loadItems();
      reset();
    }
  });

  onMount(loadOptions);
</script>

<svelte:head>
  <title>Explore - Rulate</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold mb-2">Compatibility Explorer</h1>
    <p class="text-muted-foreground">
      Explore item compatibility interactively - click on any item to see what
      it's compatible with
    </p>
  </div>

  <div class="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle>Setup</CardTitle>
        <CardDescription
          >Select catalog, ruleset, and item to explore</CardDescription
        >
      </CardHeader>
      <CardContent>
        <div class="grid gap-4 md:grid-cols-4">
          <div>
            <label for="catalog" class="block text-sm font-medium mb-2"
              >Catalog</label
            >
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
            <label for="ruleset" class="block text-sm font-medium mb-2"
              >RuleSet</label
            >
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
            <label for="item" class="block text-sm font-medium mb-2"
              >Current Item</label
            >
            <select
              id="item"
              bind:value={selectedItemId}
              class="w-full px-3 py-2 border rounded-md bg-background"
            >
              {#each items as item}
                <option value={item.item_id}>{item.name}</option>
              {/each}
            </select>
          </div>

          <div class="flex items-end">
            <Button
              onclick={() => exploreItem(selectedItemId)}
              disabled={loading}
              class="w-full"
            >
              {loading ? "Loading..." : "Explore"}
            </Button>
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

    {#if currentItem}
      <Card class="border-2 border-primary">
        <CardHeader>
          <div class="flex items-start justify-between">
            <div>
              <CardTitle class="text-2xl">{currentItem.name}</CardTitle>
              <CardDescription>{currentItem.item_id}</CardDescription>
            </div>
            <div class="text-right">
              <Badge variant="default" class="text-lg px-4 py-1">
                {compatibleResults.length} compatible
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
            {#each Object.entries(currentItem.attributes).slice(0, 8) as [key, value]}
              <div class="text-xs">
                <span class="text-muted-foreground">{key}:</span>
                <span class="font-medium ml-1">
                  {Array.isArray(value) ? value.join(", ") : value}
                </span>
              </div>
            {/each}
          </div>
        </CardContent>
      </Card>

      {#if compatibleResults.length > 0}
        <Card>
          <CardHeader>
            <CardTitle>Compatible Items</CardTitle>
            <CardDescription
              >Click on any item to explore its compatibility</CardDescription
            >
          </CardHeader>
          <CardContent>
            <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {#each compatibleResults as result}
                {@const otherId = getOtherItemId(result)}
                {@const otherItem = items.find((i) => i.item_id === otherId)}
                {#if otherItem}
                  <button
                    onclick={() => selectItem(otherId)}
                    class={compatibleItemButtonClass}
                  >
                    <div class="flex items-start justify-between mb-2">
                      <div>
                        <h4 class="font-semibold text-sm">{otherItem.name}</h4>
                        <p class="text-xs text-muted-foreground">{otherId}</p>
                      </div>
                      <Badge variant="default" class="text-xs">✓</Badge>
                    </div>
                    <div class="text-xs text-muted-foreground">
                      {result.rules_evaluated.filter((r) => r.passed)
                        .length}/{result.rules_evaluated.length} rules passed
                    </div>
                  </button>
                {/if}
              {/each}
            </div>
          </CardContent>
        </Card>
      {/if}

      {#if incompatibleResults.length > 0}
        <Card>
          <CardHeader>
            <CardTitle>Incompatible Items</CardTitle>
            <CardDescription>
              Click to explore these items - they don't match with {currentItem.name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
              {#each incompatibleResults as result}
                {@const otherId = getOtherItemId(result)}
                {@const otherItem = items.find((i) => i.item_id === otherId)}
                {#if otherItem}
                  {@const failedRules = result.rules_evaluated.filter(
                    (r) => !r.passed,
                  )}
                  <button
                    onclick={() => selectItem(otherId)}
                    class={incompatibleItemButtonClass}
                  >
                    <div class="flex items-start justify-between mb-1">
                      <div class="flex-1 min-w-0">
                        <h4 class="font-medium text-xs truncate">
                          {otherItem.name}
                        </h4>
                        <p class="text-xs text-muted-foreground truncate">
                          {otherId}
                        </p>
                      </div>
                      <Badge variant="destructive" class="text-xs ml-2">✗</Badge
                      >
                    </div>
                    <div class="mt-2 space-y-1">
                      <div class="text-xs text-muted-foreground">
                        {failedRules.length} failed {failedRules.length === 1
                          ? "rule"
                          : "rules"}:
                      </div>
                      {#each failedRules as failedRule}
                        <div
                          class="text-xs bg-destructive/10 text-destructive px-2 py-1 rounded"
                        >
                          {failedRule.rule_name}
                        </div>
                      {/each}
                    </div>
                  </button>
                {/if}
              {/each}
            </div>
          </CardContent>
        </Card>
      {/if}
    {/if}
  </div>
</div>
