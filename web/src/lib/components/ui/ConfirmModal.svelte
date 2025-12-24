<script lang="ts">
  import Modal from "./Modal.svelte";
  import Button from "./button/button.svelte";

  interface Props {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    isDanger?: boolean;
    details?: Record<string, string>;
  }

  let {
    isOpen = $bindable(false),
    onClose,
    onConfirm,
    title,
    message,
    confirmText = "Confirm",
    cancelText = "Cancel",
    isDanger = false,
    details,
  }: Props = $props();

  function handleConfirm() {
    onConfirm();
    onClose();
  }
</script>

<Modal {isOpen} {onClose} {title} size="md">
  <div class="space-y-4">
    <!-- Message -->
    <p class="text-gray-700">{message}</p>

    <!-- Details -->
    {#if details}
      <div class="rounded-lg bg-gray-50 p-4">
        <dl class="space-y-2">
          {#each Object.entries(details) as [key, value]}
            <div class="flex justify-between text-sm">
              <dt class="font-medium text-gray-600">{key}:</dt>
              <dd class="text-gray-900">{value}</dd>
            </div>
          {/each}
        </dl>
      </div>
    {/if}

    <!-- Actions -->
    <div class="flex justify-end gap-3">
      <Button variant="outline" onclick={onClose}>
        {cancelText}
      </Button>
      <Button
        variant={isDanger ? "destructive" : "default"}
        onclick={handleConfirm}
      >
        {confirmText}
      </Button>
    </div>
  </div>
</Modal>
