<!-- Copia de `@innotech/ui-svelte/components/ProgressBar.svelte` del monorepo de
     InnoTech. Se trae tal cual para que estas pantallas se vean igual que las
     de allá y para dejar de mantener una versión casera peor.

     Único cambio: ninguno.

     Si InnoTech mejora el suyo, se vuelve a copiar — mismo trato que `core/`
     en el backend y que `tokens.css`. -->
<script lang="ts" module>
  export type ProgressBarVariant = 'brand' | 'info' | 'success' | 'warning' | 'danger' | 'neutral';
</script>

<script lang="ts">
  interface Props {
    value?: number;
    max?: number;
    variant?: ProgressBarVariant;
    color?: string;
    label?: string;
    showValue?: boolean;
  }

  let {
    value = 0,
    max = 100,
    variant = 'brand',
    color,
    label,
    showValue = false,
  }: Props = $props();

  const pct = $derived(max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0);
</script>

<div class="ds-progressbar">
  <div
    class="ds-progressbar-track"
    role="progressbar"
    aria-valuenow={value}
    aria-valuemin={0}
    aria-valuemax={max}
    aria-label={label}
  >
    <div
      class="ds-progressbar-fill ds-progressbar-fill--{variant}"
      style:width="{pct}%"
      style:background={color}
    ></div>
  </div>
  {#if showValue}
    <span class="ds-progressbar-value">{Math.round(pct)}%</span>
  {/if}
</div>

<style>
  .ds-progressbar {
    display: flex;
    align-items: center;
    gap: var(--ds-space-2);
    width: 100%;
  }

  .ds-progressbar-track {
    flex: 1;
    height: 8px;
    border-radius: var(--ds-radius-full);
    background: var(--ds-neutral-200);
    overflow: hidden;
    min-width: 0;
  }

  .ds-progressbar-fill {
    height: 100%;
    border-radius: var(--ds-radius-full);
    transition: width 0.3s ease;
  }

  .ds-progressbar-fill--brand   { background: var(--ds-brand-500); }
  .ds-progressbar-fill--info    { background: var(--ds-info-500); }
  .ds-progressbar-fill--success { background: var(--ds-success-500); }
  .ds-progressbar-fill--warning { background: var(--ds-warning-500); }
  .ds-progressbar-fill--danger  { background: var(--ds-error-500); }
  .ds-progressbar-fill--neutral { background: var(--ds-neutral-400); }

  .ds-progressbar-value {
    font-size: 12px;
    font-weight: 600;
    color: var(--ds-neutral-700);
    font-variant-numeric: tabular-nums;
    min-width: 34px;
    text-align: right;
  }
</style>
