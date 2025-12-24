<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { api } from "$lib/api/client";
  import type { Schema } from "$lib/api/client";
  import Card from "$lib/components/ui/card/card.svelte";
  import CardHeader from "$lib/components/ui/card/card-header.svelte";
  import CardTitle from "$lib/components/ui/card/card-title.svelte";
  import CardDescription from "$lib/components/ui/card/card-description.svelte";
  import CardContent from "$lib/components/ui/card/card-content.svelte";
  import Button from "$lib/components/ui/button/button.svelte";
  import Badge from "$lib/components/ui/badge/badge.svelte";
  import Skeleton from "$lib/components/ui/skeleton/skeleton.svelte";

  let schema = $state<Schema | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);

  let schemaName = $derived($page.params.name ?? "");
  let pageTitle = $derived(`${schemaName} - Schema - Rulate`);

  async function loadSchema() {
    try {
      loading = true;
      error = null;
      schema = await api.getSchema(schemaName);
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load schema";
    } finally {
      loading = false;
    }
  }

  onMount(loadSchema);
</script>

<svelte:head>
  <title>{pageTitle}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="mb-6">
    <Button href="/schemas" variant="ghost" size="sm">← Back to Schemas</Button>
  </div>

  {#if error}
    <Card class="border-destructive">
      <CardHeader>
        <CardTitle>Error</CardTitle>
        <CardDescription>{error}</CardDescription>
      </CardHeader>
      <CardContent>
        <Button onclick={loadSchema}>Retry</Button>
      </CardContent>
    </Card>
  {:else if loading}
    <Card>
      <CardHeader>
        <Skeleton class="h-8 w-64 mb-2" />
        <Skeleton class="h-4 w-32" />
      </CardHeader>
      <CardContent>
        <Skeleton class="h-64 w-full" />
      </CardContent>
    </Card>
  {:else if schema}
    <div class="space-y-6">
      <Card>
        <CardHeader>
          <div class="flex items-start justify-between">
            <div>
              <CardTitle class="text-3xl">{schema.name}</CardTitle>
              <CardDescription>Version {schema.version}</CardDescription>
            </div>
            <Badge variant="secondary"
              >{schema.dimensions.length} dimensions</Badge
            >
          </div>
        </CardHeader>
        <CardContent>
          {#if schema.created_at}
            <p class="text-sm text-muted-foreground mb-4">
              Created {new Date(schema.created_at).toLocaleString()}
            </p>
          {/if}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Dimensions</CardTitle>
          <CardDescription>
            Field definitions and validation rules for items using this schema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            {#each schema.dimensions as dimension}
              <div class="border rounded-lg p-4">
                <div class="flex items-start justify-between mb-2">
                  <div>
                    <h4 class="font-semibold">{dimension.name}</h4>
                    <div class="flex gap-2 mt-1">
                      <Badge variant="outline">{dimension.type}</Badge>
                      {#if dimension.required}
                        <Badge variant="destructive">Required</Badge>
                      {:else}
                        <Badge variant="secondary">Optional</Badge>
                      {/if}
                    </div>
                  </div>
                </div>

                <div class="text-sm text-muted-foreground mt-2 space-y-1">
                  {#if dimension.type === "enum" && dimension.values}
                    <p>
                      <span class="font-medium">Values:</span>
                      {dimension.values.join(", ")}
                    </p>
                  {/if}

                  {#if dimension.type === "integer" || dimension.type === "float"}
                    {#if dimension.min !== undefined}
                      <p>
                        <span class="font-medium">Min:</span>
                        {dimension.min}
                      </p>
                    {/if}
                    {#if dimension.max !== undefined}
                      <p>
                        <span class="font-medium">Max:</span>
                        {dimension.max}
                      </p>
                    {/if}
                  {/if}

                  {#if dimension.type === "list" && dimension.item_type}
                    <p>
                      <span class="font-medium">Item Type:</span>
                      {dimension.item_type}
                    </p>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </CardContent>
      </Card>
    </div>
  {/if}
</div>
