<script lang="ts">
  import { goto } from "$app/navigation";
  import { api } from "$lib/api/client";
  import type { Dimension } from "$lib/api/client";
  import Card from "$lib/components/ui/card/card.svelte";
  import CardHeader from "$lib/components/ui/card/card-header.svelte";
  import CardTitle from "$lib/components/ui/card/card-title.svelte";
  import CardDescription from "$lib/components/ui/card/card-description.svelte";
  import CardContent from "$lib/components/ui/card/card-content.svelte";
  import Button from "$lib/components/ui/button/button.svelte";
  import Badge from "$lib/components/ui/badge/badge.svelte";

  let name = $state("");
  let version = $state("1.0.0");
  let dimensions = $state<Dimension[]>([]);
  let error = $state<string | null>(null);
  let submitting = $state(false);

  function addDimension() {
    dimensions = [
      ...dimensions,
      {
        name: "",
        type: "string",
        required: false,
      },
    ];
  }

  function removeDimension(index: number) {
    dimensions = dimensions.filter((_, i) => i !== index);
  }

  function updateDimension(index: number, updates: Partial<Dimension>) {
    dimensions = dimensions.map((dim, i) =>
      i === index ? { ...dim, ...updates } : dim,
    );
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    console.log("Schema form submitted!");
    console.log("Name:", name);
    console.log("Version:", version);
    console.log("Dimensions:", dimensions);

    error = null;

    // Validate
    if (!name.trim()) {
      error = "Schema name is required";
      console.error("Validation failed: name is required");
      return;
    }

    if (dimensions.length === 0) {
      error = "At least one dimension is required";
      console.error("Validation failed: no dimensions");
      return;
    }

    for (const dim of dimensions) {
      if (!dim.name.trim()) {
        error = "All dimensions must have a name";
        console.error("Validation failed: dimension missing name");
        return;
      }
    }

    try {
      submitting = true;
      console.log("Calling API to create schema...");
      const result = await api.createSchema({
        name: name.trim(),
        version: version.trim(),
        dimensions,
      });
      console.log("API response:", result);
      console.log("Navigating to schema detail page...");
      goto(`/schemas/${name.trim()}`);
    } catch (err) {
      console.error("API error:", err);
      error = err instanceof Error ? err.message : "Failed to create schema";
      submitting = false;
    }
  }
</script>

<svelte:head>
  <title>Create Schema - Rulate</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-7xl">
  <div class="mb-8">
    <h1 class="text-4xl font-bold mb-2">Create Schema</h1>
    <p class="text-muted-foreground">
      Define the structure and validation rules for your items
    </p>
  </div>

  <form onsubmit={handleSubmit}>
    <div class="space-y-6">
      <!-- Basic Info -->
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
          <CardDescription>Schema name and version</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div>
              <label for="name" class="block text-sm font-medium mb-2"
                >Name</label
              >
              <input
                type="text"
                id="name"
                name="name"
                bind:value={name}
                class="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., wardrobe_schema"
                required
              />
            </div>
            <div>
              <label for="version" class="block text-sm font-medium mb-2"
                >Version</label
              >
              <input
                type="text"
                id="version"
                name="version"
                bind:value={version}
                class="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="1.0.0"
                required
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Dimensions -->
      <Card>
        <CardHeader>
          <div class="flex items-start justify-between">
            <div>
              <CardTitle>Dimensions</CardTitle>
              <CardDescription
                >Define the attributes that items can have</CardDescription
              >
            </div>
            <Button type="button" onclick={addDimension} size="sm"
              >Add Dimension</Button
            >
          </div>
        </CardHeader>
        <CardContent>
          {#if dimensions.length === 0}
            <div class="text-center py-8 text-muted-foreground">
              <p>No dimensions defined yet</p>
              <p class="text-sm mt-2">Click "Add Dimension" to get started</p>
            </div>
          {:else}
            <div class="space-y-4">
              {#each dimensions as dim, index}
                <div class="border border-border rounded-lg p-4">
                  <div class="flex items-start justify-between mb-4">
                    <Badge variant="outline">Dimension {index + 1}</Badge>
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      onclick={() => removeDimension(index)}>Remove</Button
                    >
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Name -->
                    <div>
                      <label
                        for="dim-name-{index}"
                        class="block text-sm font-medium mb-2">Name</label
                      >
                      <input
                        id="dim-name-{index}"
                        type="text"
                        bind:value={dim.name}
                        onchange={(e) =>
                          updateDimension(index, {
                            name: e.currentTarget.value,
                          })}
                        class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                        placeholder="e.g., color"
                        required
                      />
                    </div>

                    <!-- Type -->
                    <div>
                      <label
                        for="dim-type-{index}"
                        class="block text-sm font-medium mb-2">Type</label
                      >
                      <select
                        id="dim-type-{index}"
                        bind:value={dim.type}
                        onchange={(e) =>
                          updateDimension(index, {
                            type: e.currentTarget.value as Dimension["type"],
                          })}
                        class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                      >
                        <option value="string">String</option>
                        <option value="integer">Integer</option>
                        <option value="float">Float</option>
                        <option value="boolean">Boolean</option>
                        <option value="enum">Enum</option>
                        <option value="list">List</option>
                      </select>
                    </div>

                    <!-- Required -->
                    <div class="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="required-{index}"
                        bind:checked={dim.required}
                        onchange={(e) =>
                          updateDimension(index, {
                            required: e.currentTarget.checked,
                          })}
                        class="rounded border-input"
                      />
                      <label for="required-{index}" class="text-sm font-medium"
                        >Required</label
                      >
                    </div>

                    <!-- Type-specific fields -->
                    {#if dim.type === "enum"}
                      <div class="md:col-span-2">
                        <label
                          for="dim-values-{index}"
                          class="block text-sm font-medium mb-2"
                          >Allowed Values (comma-separated)</label
                        >
                        <input
                          id="dim-values-{index}"
                          type="text"
                          value={dim.values?.join(", ") || ""}
                          oninput={(e) =>
                            updateDimension(index, {
                              values: e.currentTarget.value
                                .split(",")
                                .map((v) => v.trim())
                                .filter((v) => v),
                            })}
                          class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                          placeholder="e.g., red, blue, green"
                        />
                      </div>
                    {:else if dim.type === "integer" || dim.type === "float"}
                      <div>
                        <label
                          for="dim-min-{index}"
                          class="block text-sm font-medium mb-2"
                          >Min Value</label
                        >
                        <input
                          id="dim-min-{index}"
                          type="number"
                          bind:value={dim.min}
                          step={dim.type === "float" ? "0.1" : "1"}
                          onchange={(e) =>
                            updateDimension(index, {
                              min: e.currentTarget.value
                                ? parseFloat(e.currentTarget.value)
                                : undefined,
                            })}
                          class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                        />
                      </div>
                      <div>
                        <label
                          for="dim-max-{index}"
                          class="block text-sm font-medium mb-2"
                          >Max Value</label
                        >
                        <input
                          id="dim-max-{index}"
                          type="number"
                          bind:value={dim.max}
                          step={dim.type === "float" ? "0.1" : "1"}
                          onchange={(e) =>
                            updateDimension(index, {
                              max: e.currentTarget.value
                                ? parseFloat(e.currentTarget.value)
                                : undefined,
                            })}
                          class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                        />
                      </div>
                    {:else if dim.type === "list"}
                      <div class="md:col-span-2">
                        <label
                          for="dim-item-type-{index}"
                          class="block text-sm font-medium mb-2"
                          >Item Type</label
                        >
                        <select
                          id="dim-item-type-{index}"
                          bind:value={dim.item_type}
                          onchange={(e) =>
                            updateDimension(index, {
                              item_type: e.currentTarget.value,
                            })}
                          class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                        >
                          <option value="string">String</option>
                          <option value="integer">Integer</option>
                          <option value="float">Float</option>
                          <option value="boolean">Boolean</option>
                        </select>
                      </div>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </CardContent>
      </Card>

      <!-- Error Display -->
      {#if error}
        <Card class="border-destructive">
          <CardContent class="pt-6">
            <p class="text-destructive">{error}</p>
          </CardContent>
        </Card>
      {/if}

      <!-- Actions -->
      <div class="flex gap-3">
        <Button type="submit" disabled={submitting}>
          {submitting ? "Creating..." : "Create Schema"}
        </Button>
        <Button type="button" variant="outline" href="/schemas">Cancel</Button>
      </div>
    </div>
  </form>
</div>
