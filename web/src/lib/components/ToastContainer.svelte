<script lang="ts">
  import { toastStore } from "$lib/stores/toast.svelte";
  import Toast from "./ui/Toast.svelte";
</script>

{#if toastStore.toasts.length > 0}
  <div
    class="fixed right-4 top-4 z-50 flex flex-col gap-2"
    aria-label="Notifications"
    role="region"
  >
    {#each toastStore.toasts as toast (toast.id)}
      <Toast
        message={toast.message}
        type={toast.type}
        onClose={() => toastStore.removeToast(toast.id)}
      />
    {/each}
  </div>
{/if}
