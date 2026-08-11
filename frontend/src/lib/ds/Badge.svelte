<script lang="ts">
  /* Etiqueta de estado.
   *
   * Firma alineada con `@innotech/ui-svelte/Badge`: `variant`, `size`, `pill`
   * y el snippet `children`.
   */
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
    size?: 'sm' | 'md' | 'lg';
    pill?: boolean;
    class?: string;
    children?: Snippet;
  }

  let {
    variant = 'primary',
    size = 'md',
    pill = true,
    class: customClass = '',
    children,
  }: Props = $props();
</script>

<span class="ds-badge ds-badge-{variant} ds-badge-{size} {customClass}" class:is-pill={pill}>
  {#if children}{@render children()}{/if}
</span>

<style>
  .ds-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-weight: 600; border-radius: 6px; white-space: nowrap;
  }
  .is-pill { border-radius: 999px; }

  .ds-badge-sm { padding: 2px 8px; font-size: 10px; }
  .ds-badge-md { padding: 3px 10px; font-size: 11px; }
  .ds-badge-lg { padding: 5px 12px; font-size: 13px; }

  .ds-badge-primary { background: var(--ds-brand-100); color: var(--ds-brand-600); }
  .ds-badge-success { background: var(--ds-success-100); color: var(--ds-success-700); }
  .ds-badge-warning { background: var(--ds-warning-100); color: var(--ds-warning-700); }
  .ds-badge-error   { background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700); }
  .ds-badge-info    { background: #eff6ff; color: #1d4ed8; }
  .ds-badge-neutral { background: var(--ds-neutral-200, #f1f5f9); color: var(--ds-neutral-600, #475569); }
</style>
