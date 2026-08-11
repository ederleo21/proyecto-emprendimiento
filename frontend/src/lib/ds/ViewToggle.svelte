<!-- Copia de `@innotech/ui-svelte/components/ViewToggle.svelte` del monorepo de
     InnoTech. Se trae tal cual para que estas pantallas se vean igual que las
     de allá y para dejar de mantener una versión casera peor.

     Único cambio: los nombres de icono (`base/hamburger-button` y
     `base/rectangle-button` no existen en nuestro `Icon`; se usan
     `interface/list` e `interface/grid`) y se quitó una clase de Tailwind,
     que este proyecto no usa.

     Si InnoTech mejora el suyo, se vuelve a copiar — mismo trato que `core/`
     en el backend y que `tokens.css`. -->
<script lang="ts">
  // Switch Tabla / Tarjetas reutilizable. Mismo look que el de
  // Instituciones / Proyectos Academicos. Bindable: bind:value.
  import Icon from './Icon.svelte';

  let { value = $bindable<'table' | 'card'>('table') } = $props();
</script>

<div class="view-toggle" role="group" aria-label="Modo de visualización">
  <button
    type="button"
    class="view-toggle-btn"
    class:active={value === 'table'}
    onclick={() => (value = 'table')}
    title="Vista en tabla"
    aria-label="Vista en tabla"
    aria-pressed={value === 'table'}
  >
    <Icon name="interface/list" size="sm" />
  </button>
  <button
    type="button"
    class="view-toggle-btn"
    class:active={value === 'card'}
    onclick={() => (value = 'card')}
    title="Vista en tarjetas"
    aria-label="Vista en tarjetas"
    aria-pressed={value === 'card'}
  >
    <Icon name="interface/grid" size="sm" />
  </button>
</div>

<style>
  .view-toggle {
    display: inline-flex;
    align-items: center;
    background: var(--ds-neutral-100);
    border: 1px solid var(--ds-neutral-200);
    border-radius: 8px;
    padding: 2px;
    gap: 2px;
  }

  .view-toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: var(--ds-neutral-500);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .view-toggle-btn:hover:not(.active) {
    background: var(--ds-neutral-200);
    color: var(--ds-neutral-700);
  }

  .view-toggle-btn.active {
    background: #ffffff;
    color: var(--ds-brand-500);
    box-shadow: var(--ds-shadow-xs);
  }
</style>
