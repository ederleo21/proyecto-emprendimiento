<script lang="ts">
  /* Botón.
   *
   * Firma alineada con `@innotech/ui-svelte/Button`: mismos nombres de props y
   * mismos valores. Solo se implementaron las variantes que las pantallas
   * usan; agregar otra es sumar una rama al mapa de colores.
   *
   * Los colores salen de los tokens (`--ds-*`), nunca de un hex acá: por eso
   * el botón primario toma el color que configure la institución.
   */
  import type { Snippet } from 'svelte';

  interface Props {
    label?: string;
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
    size?: 'sm' | 'md' | 'lg';
    type?: 'button' | 'submit' | 'reset';
    loading?: boolean;
    disabled?: boolean;
    fullWidth?: boolean;
    class?: string;
    prefix?: Snippet;
    children?: Snippet;
    suffix?: Snippet;
    onclick?: (e: MouseEvent) => void;
    [key: string]: any;
  }

  let {
    label = '',
    variant = 'primary',
    size = 'md',
    type = 'button',
    loading = false,
    disabled = false,
    fullWidth = false,
    class: customClass = '',
    prefix,
    children,
    suffix,
    onclick,
    ...rest
  }: Props = $props();
</script>

<button
  {type}
  class="ds-btn ds-btn-{variant} ds-btn-{size} {customClass}"
  class:is-full={fullWidth}
  class:is-loading={loading}
  disabled={disabled || loading}
  {onclick}
  {...rest}
>
  {#if loading}<span class="ds-btn-spinner" aria-hidden="true"></span>{/if}
  {#if prefix}{@render prefix()}{/if}
  {#if children}{@render children()}{:else if label}{label}{/if}
  {#if suffix}{@render suffix()}{/if}
</button>

<style>
  .ds-btn {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    border: 1.5px solid transparent; border-radius: 8px;
    font-family: inherit; font-weight: 600; cursor: pointer; white-space: nowrap;
    transition: background 0.18s, color 0.18s, border-color 0.18s;
  }
  .ds-btn:disabled { opacity: 0.55; cursor: not-allowed; }
  .is-full { width: 100%; }

  .ds-btn-sm { padding: 6px 12px; font-size: 12px; }
  .ds-btn-md { padding: 9px 16px; font-size: 13px; }
  .ds-btn-lg { padding: 12px 22px; font-size: 15px; }

  /* Primario = color de marca, o sea el que configuró la institución. */
  .ds-btn-primary {
    background: var(--ds-brand-500); color: #fff; border-color: var(--ds-brand-500);
  }
  .ds-btn-primary:hover:not(:disabled) {
    background: var(--ds-brand-600); border-color: var(--ds-brand-600);
  }
  .ds-btn-secondary {
    background: var(--ds-brand-100); color: var(--ds-brand-600);
    border-color: var(--ds-brand-100);
  }
  .ds-btn-secondary:hover:not(:disabled) { background: var(--ds-brand-300); }
  .ds-btn-outline {
    background: #fff; color: var(--ds-neutral-700, #334155);
    border-color: var(--ds-neutral-300, #e2e8f0);
  }
  .ds-btn-outline:hover:not(:disabled) { background: var(--ds-neutral-100, #f1f5f9); }
  .ds-btn-ghost { background: transparent; color: var(--ds-neutral-600, #475569); }
  .ds-btn-ghost:hover:not(:disabled) { background: var(--ds-neutral-100, #f1f5f9); }
  .ds-btn-danger {
    background: var(--ds-error-500); color: #fff; border-color: var(--ds-error-500);
  }
  .ds-btn-danger:hover:not(:disabled) { background: var(--ds-error-600); }
  .ds-btn-success {
    background: var(--ds-success-500); color: #fff; border-color: var(--ds-success-500);
  }

  .ds-btn-spinner {
    width: 13px; height: 13px; border-radius: 50%;
    border: 2px solid currentColor; border-top-color: transparent;
    animation: ds-spin 0.6s linear infinite;
  }
  @keyframes ds-spin { to { transform: rotate(360deg); } }
</style>
