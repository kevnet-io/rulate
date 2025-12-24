<script lang="ts">
  import { page } from "$app/stores";
  import ThemeToggle from "$lib/components/ui/ThemeToggle.svelte";

  const navItems = [
    { href: "/", label: "Home" },
    { href: "/catalogs", label: "Catalogs" },
    { href: "/schemas", label: "Schemas" },
    { href: "/rulesets", label: "RuleSets" },
    { href: "/cluster-rulesets", label: "Cluster RuleSets" },
    { href: "/explore", label: "Explorer" },
    { href: "/matrix", label: "Matrix" },
    { href: "/clusters", label: "Clusters" },
    { href: "/import-export", label: "Import/Export" },
  ];

  function isActive(path: string): boolean {
    if (path === "/") {
      return $page.url.pathname === "/";
    }
    return $page.url.pathname.startsWith(path);
  }
</script>

<nav
  class="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
>
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center gap-8">
        <a href="/" class="text-xl font-bold text-foreground">Rulate</a>
        <div class="flex gap-1">
          {#each navItems as item}
            <a
              href={item.href}
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors {isActive(
                item.href,
              )
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'}"
            >
              {item.label}
            </a>
          {/each}
        </div>
      </div>
      <div class="flex items-center gap-4">
        <ThemeToggle />
      </div>
    </div>
  </div>
</nav>
