<script lang="ts">
  /* Modal.
   *
   * Firma alineada con `@innotech/ui-svelte/Modal`: `open` bindable, `title`,
   * `size`, `closeOnOutsideClick`, y los snippets `children` y `footer`.
   */
  import type { Snippet } from 'svelte';

  interface Props {
    open?: boolean;
    title?: string;
    size?: 'sm' | 'md' | 'lg';
    closeOnOutsideClick?: boolean;
    children?: Snippet;
    footer?: Snippet;
  }

  let {
    open = $bindable(false),
    title = '',
    size = 'md',
    closeOnOutsideClick = true,
    children,
    footer,
  }: Props = $props();

  function onOverlayClick() {
    if (closeOnOutsideClick) open = false;
  }

  // Escape cierra: es lo que espera cualquiera que use un modal.
  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) open = false;
  }
</script>

<svelte:window onkeydown={onKeydown} />

{#if open}
  <!-- El overlay es clicable pero no es un control: el cierre accesible va
       por el botón × y por Escape. -->
  <div
    class="ds-overlay"
    role="presentation"
    onclick={onOverlayClick}
  >
    <div
      class="ds-modal ds-modal-{size}"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onclick={(e) => e.stopPropagation()}
    >
      <header class="ds-modal-head">
        <h3>{title}</h3>
        <button class="ds-modal-close" onclick={() => (open = false)} aria-label="Cerrar">
          &times;
        </button>
      </header>

      <div class="ds-modal-body">
        {#if children}{@render children()}{/if}
      </div>

      {#if footer}
        <footer class="ds-modal-foot">{@render footer()}</footer>
      {/if}
    </div>
  </div>
{/if}

<style>
  .ds-overlay {
    position: fixed; inset: 0; z-index: 1000;
    background: rgba(15, 23, 42, 0.45);
    display: flex; align-items: center; justify-content: center; padding: 24px;
  }
  .ds-modal {
    background: #fff; border-radius: 14px; width: 100%;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.22);
    display: flex; flex-direction: column; max-height: 90vh;
  }
  .ds-modal-sm { max-width: 420px; }
  .ds-modal-md { max-width: 560px; }
  .ds-modal-lg { max-width: 820px; }

  .ds-modal-head {
    display: flex; align-items: center; gap: 12px;
    padding: 16px 20px; border-bottom: 1px solid var(--ds-neutral-200, #eef2f6);
  }
  .ds-modal-head h3 {
    margin: 0; flex: 1; font-size: 16px; font-weight: 700;
    color: var(--ds-neutral-800, #1e293b);
  }
  .ds-modal-close {
    border: 0; background: transparent; font-size: 24px; line-height: 1;
    color: var(--ds-neutral-500, #64748b); cursor: pointer; padding: 0 4px;
  }
  .ds-modal-close:hover { color: var(--ds-neutral-800, #1e293b); }

  .ds-modal-body { padding: 20px; overflow-y: auto; }
  .ds-modal-foot {
    display: flex; justify-content: flex-end; gap: 8px;
    padding: 14px 20px; border-top: 1px solid var(--ds-neutral-200, #eef2f6);
  }
</style>
