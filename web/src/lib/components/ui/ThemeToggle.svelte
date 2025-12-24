<script lang="ts">
  import { themeStore } from "$lib/stores/theme.svelte";
  import Tooltip from "./Tooltip.svelte";

  function getThemeIcon(theme: string): string {
    switch (theme) {
      case "light":
        return "☀️";
      case "dark":
        return "🌙";
      case "system":
        return "💻";
      default:
        return "💻";
    }
  }

  function getThemeLabel(theme: string): string {
    switch (theme) {
      case "light":
        return "Light mode";
      case "dark":
        return "Dark mode";
      case "system":
        return "System theme";
      default:
        return "System theme";
    }
  }

  function handleToggle() {
    themeStore.toggle();
  }
</script>

<Tooltip text={getThemeLabel(themeStore.theme)} position="bottom">
  <button
    onclick={handleToggle}
    class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring hover:bg-accent hover:text-accent-foreground h-9 w-9"
    aria-label="Toggle theme"
    type="button"
  >
    <span class="text-lg" aria-hidden="true">
      {getThemeIcon(themeStore.theme)}
    </span>
  </button>
</Tooltip>
