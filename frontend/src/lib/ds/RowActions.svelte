<!-- Copia de `@innotech/ui-svelte/components/RowActions.svelte` del monorepo de
     InnoTech. Sin cambios. -->
<script lang="ts" module>
  /**
   * Acciones de fila reutilizable para cualquier tabla del DS InnoTech 2.0.
   *
   * Estética: iconos planos sin bordes, color info-600 (#1A85FF).
   * Cuando `expanded` es true muestra todos los íconos en línea más el
   * kebab "⋮". Cuando es false muestra solo el kebab que abre un menú
   * con la misma lista (icono + texto).
   *
   * `actions` puede incluir items con `hidden: true` para esa fila.
   */
  export interface RowAction {
    icon: string;
    title: string;
    onclick: () => void;
    hidden?: boolean;
    disabled?: boolean;
  }
</script>

<script lang="ts">
  import Icon from './Icon.svelte';
  import Tooltip from './Tooltip.svelte';

  interface Props {
    actions: RowAction[];
    expanded: boolean;
  }
  let { actions, expanded }: Props = $props();

  const visible = $derived(actions.filter((a) => !a.hidden));

  let menuOpen = $state(false);
  let menuRef: HTMLDivElement | null = $state(null);
  let kebabBtnRef: HTMLButtonElement | null = $state(null);
  let menuStyle = $state('');

  function placeMenu() {
    if (!kebabBtnRef) return;
    const r = kebabBtnRef.getBoundingClientRect();
    // Portal con position:fixed para escapar de cualquier overflow:hidden
    // del wrapper de la tabla. Mismo patrón que el Tooltip del DS.
    menuStyle = `position: fixed; top: ${r.bottom + 6}px; right: ${window.innerWidth - r.right}px; z-index: 9999;`;
  }

  function toggleMenu() {
    if (!menuOpen) placeMenu();
    menuOpen = !menuOpen;
  }
  function closeMenu() { menuOpen = false; }
  function onAction(a: RowAction) { a.onclick(); closeMenu(); }

  function onWindowClick(e: MouseEvent) {
    if (!menuOpen) return;
    const target = e.target as Node;
    if (menuRef && menuRef.contains(target)) return;
    if (kebabBtnRef && kebabBtnRef.contains(target)) return;
    menuOpen = false;
  }
  function onScroll() { if (menuOpen) menuOpen = false; }

  // Mueve el menú a document.body: un `position:fixed` normal no basta si
  // algún ancestro (ej. una celda `position: sticky` de tabla) crea su
  // propio stacking context, porque entonces el z-index del menú queda
  // acotado dentro de ese contexto y filas/columnas posteriores lo tapan.
  // Mismo patrón que el portal del Tooltip del DS.
  function portal(node: HTMLElement) {
    document.body.appendChild(node);
    return {
      destroy() {
        if (node.isConnected) node.remove();
      }
    };
  }
</script>

<svelte:window onclick={onWindowClick} onscroll={onScroll} onresize={onScroll} />

<div class="row-actions" class:row-actions--collapsed={!expanded}>
  {#if expanded}
    {#each visible as a}
      <Tooltip content={a.title} position="top">
        <button type="button" class="ra-btn" disabled={a.disabled}
                onclick={a.onclick} aria-label={a.title}>
          <Icon name={a.icon} size="sm" />
        </button>
      </Tooltip>
    {/each}
  {:else}
    <Tooltip content="Más acciones" position="top">
      <button type="button" class="ra-btn" bind:this={kebabBtnRef}
              aria-label="Más acciones" aria-expanded={menuOpen}
              onclick={toggleMenu}>
        <Icon name="interface/dots-vertical" size="sm" />
      </button>
    </Tooltip>
  {/if}
</div>

{#if menuOpen}
  <div use:portal class="kebab__menu" role="menu" style={menuStyle} bind:this={menuRef}>
    {#each visible as a}
      <button type="button" class="kebab__item" role="menuitem"
              disabled={a.disabled} onclick={() => onAction(a)}>
        <Icon name={a.icon} size="sm" />
        <span>{a.title}</span>
      </button>
    {/each}
  </div>
{/if}

<style>
  .row-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    width: 100%;
  }
  /* Cuando solo se muestra el kebab (modo colapsado), centramos para
     evitar el espacio en blanco a la izquierda de la celda. */
  .row-actions--collapsed { justify-content: center; }
  .ra-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: transparent;
    border: none;
    padding: 0;
    color: var(--ds-info-600);
    cursor: pointer;
    transition: opacity 0.15s ease;
  }
  .ra-btn:hover:not(:disabled) { opacity: 0.7; }
  .ra-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .kebab__menu {
    min-width: 200px;
    background: white;
    border: 1px solid var(--ds-info-300);
    border-radius: var(--ds-radius-md);
    box-shadow: var(--ds-shadow-md);
    padding: 4px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .kebab__item {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: transparent;
    border: none;
    border-radius: var(--ds-radius-sm);
    color: var(--ds-neutral-700);
    font-size: 13px;
    font-weight: 500;
    text-align: left;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s ease;
  }
  /* Los iconos siguen en celeste para mantener la identidad visual. */
  .kebab__item :global(svg) { color: var(--ds-info-600); }
  .kebab__item:hover:not(:disabled) {
    background: var(--ds-neutral-100);
    color: var(--ds-neutral-900);
  }
  .kebab__item:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
