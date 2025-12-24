<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { api } from "$lib/api/client";
  import type { Catalog, Item, Schema } from "$lib/api/client";
  import { toastStore } from "$lib/stores/toast.svelte";
  import Card from "$lib/components/ui/card/card.svelte";
  import CardHeader from "$lib/components/ui/card/card-header.svelte";
  import CardTitle from "$lib/components/ui/card/card-title.svelte";
  import CardDescription from "$lib/components/ui/card/card-description.svelte";
  import CardContent from "$lib/components/ui/card/card-content.svelte";
  import Button from "$lib/components/ui/button/button.svelte";
  import Badge from "$lib/components/ui/badge/badge.svelte";
  import Skeleton from "$lib/components/ui/skeleton/skeleton.svelte";
  import ConfirmModal from "$lib/components/ui/ConfirmModal.svelte";

  let catalog = $state<Catalog | null>(null);
  let items = $state<Item[]>([]);
  let _schema = $state<Schema | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let showDeleteModal = $state(false);
  let itemToDelete = $state<string | null>(null);

  let catalogName = $derived($page.params.name ?? "");
  let pageTitle = $derived(`${catalogName} - Catalog - Rulate`);

  async function loadData() {
    try {
      loading = true;
      error = null;
      catalog = await api.getCatalog(catalogName);
      items = await api.getItems(catalogName);
      if (catalog) {
        _schema = await api.getSchema(catalog.schema_name);
      }
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load catalog";
      toastStore.error(error);
    } finally {
      loading = false;
    }
  }

  function confirmDelete(itemId: string) {
    itemToDelete = itemId;
    showDeleteModal = true;
  }

  async function deleteItem() {
    if (!itemToDelete) return;

    try {
      await api.deleteItem(catalogName, itemToDelete);
      toastStore.success(`Item "${itemToDelete}" deleted successfully`);
      await loadData();
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to delete item";
      toastStore.error(errorMsg);
    }
  }

  onMount(loadData);
</script>

<svelte:head>
  <title>{pageTitle}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="mb-6">
    <Button href="/catalogs" variant="ghost" size="sm"
      >← Back to Catalogs</Button
    >
  </div>

  {#if error}
    <Card class="border-destructive">
      <CardHeader>
        <CardTitle>Error</CardTitle>
        <CardDescription>{error}</CardDescription>
      </CardHeader>
      <CardContent>
        <Button onclick={loadData}>Retry</Button>
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
  {:else if catalog}
    <div class="space-y-6">
      <Card>
        <CardHeader>
          <div class="flex items-start justify-between">
            <div>
              <CardTitle class="text-3xl">{catalog.name}</CardTitle>
              <CardDescription>
                {catalog.description || "No description"}
              </CardDescription>
            </div>
            <Badge variant="secondary">{items.length} items</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <p class="text-sm">
              <span class="text-muted-foreground">Schema:</span>
              <a
                href="/schemas/{catalog.schema_name}"
                class="font-medium text-primary hover:underline ml-2"
              >
                {catalog.schema_name}
              </a>
            </p>
            {#if catalog.created_at}
              <p class="text-sm text-muted-foreground">
                Created {new Date(catalog.created_at).toLocaleString()}
              </p>
            {/if}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <div>
              <CardTitle>Items</CardTitle>
              <CardDescription>Items in this catalog</CardDescription>
            </div>
            <Button href="/catalogs/{catalogName}/items/new">Add Item</Button>
          </div>
        </CardHeader>
        <CardContent>
          {#if items.length === 0}
            <div class="text-center py-8">
              <p class="text-muted-foreground mb-4">
                No items in this catalog yet
              </p>
              <Button href="/catalogs/{catalogName}/items/new"
                >Add First Item</Button
              >
            </div>
          {:else}
            <div class="grid gap-4 md:grid-cols-2">
              {#each items as item}
                <div class="border rounded-lg p-4">
                  <div class="flex items-start justify-between mb-2">
                    <div class="flex-1">
                      <h4 class="font-semibold">{item.name}</h4>
                      <p class="text-xs text-muted-foreground">
                        {item.item_id}
                      </p>
                    </div>
                  </div>

                  <div class="mt-3 space-y-1">
                    <p class="text-xs font-medium text-muted-foreground mb-1">
                      Attributes:
                    </p>
                    <div class="flex flex-wrap gap-1">
                      {#each Object.entries(item.attributes).slice(0, 4) as [key, value]}
                        <Badge variant="outline" class="text-xs">
                          {key}:
                          {Array.isArray(value) ? value.join(", ") : value}
                        </Badge>
                      {/each}
                      {#if Object.keys(item.attributes).length > 4}
                        <Badge variant="outline" class="text-xs">
                          +{Object.keys(item.attributes).length - 4} more
                        </Badge>
                      {/if}
                    </div>
                  </div>

                  <div class="flex gap-2 mt-4">
                    <Button
                      href="/catalogs/{catalogName}/items/{item.item_id}"
                      variant="outline"
                      size="sm">View Details</Button
                    >
                    <Button
                      variant="destructive"
                      size="sm"
                      onclick={() => confirmDelete(item.item_id)}>Delete</Button
                    >
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </CardContent>
      </Card>
    </div>
  {/if}
</div>

<ConfirmModal
  bind:isOpen={showDeleteModal}
  onClose={() => (showDeleteModal = false)}
  onConfirm={deleteItem}
  title="Delete Item"
  message="Are you sure you want to delete this item? This action cannot be undone."
  confirmText="Delete"
  isDanger={true}
  details={itemToDelete ? { ID: itemToDelete } : undefined}
/>
