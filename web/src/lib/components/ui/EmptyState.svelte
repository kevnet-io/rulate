<script lang="ts">
  import Button from "./button/button.svelte";
  import Card from "./card/card.svelte";
  import CardHeader from "./card/card-header.svelte";
  import CardTitle from "./card/card-title.svelte";
  import CardDescription from "./card/card-description.svelte";
  import CardContent from "./card/card-content.svelte";

  interface Props {
    title: string;
    description: string;
    actionText?: string;
    actionHref?: string;
    icon?: string;
  }

  let { title, description, actionText, actionHref, icon }: Props = $props();
</script>

<Card class="text-center">
  <CardHeader>
    {#if icon}
      <div
        class="mx-auto mb-4 text-6xl text-muted-foreground/30"
        aria-hidden="true"
      >
        {icon}
      </div>
    {/if}
    <CardTitle>{title}</CardTitle>
    <CardDescription>{description}</CardDescription>
  </CardHeader>
  {#if actionText && actionHref}
    <CardContent>
      <Button href={actionHref}>{actionText}</Button>
    </CardContent>
  {/if}
</Card>
