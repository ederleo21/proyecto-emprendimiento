<!-- Copia de `@innotech/ui-svelte/components/inputs/Checkbox.svelte` del monorepo de InnoTech.
     Sin cambios. Trae sus propias transiciones. -->
<script lang="ts">
  export let checked = false;
  export let label = "";
  export let id = Math.random().toString(36).substring(7);
  export let disabled = false;
  /** Color de la casilla marcada. `success` para confirmaciones. */
  export let tone: "info" | "success" = "info";
  /** Se dispara con el nuevo valor. Complementa a `bind:checked`. */
  export let onchange: ((checked: boolean) => void) | undefined = undefined;
</script>

<div class="ds-checkbox-container ds-checkbox--{tone}" class:is-disabled={disabled}>
  <input
    type="checkbox"
    {id}
    {disabled}
    bind:checked
    class="ds-checkbox-input"
    on:change={(e) => onchange?.(e.currentTarget.checked)}
  />
  <label for={id} class="ds-checkbox-label">
    <div class="checkbox-visual">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" class="check-icon">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
    </div>
    {#if label}
      <span class="label-text">{label}</span>
    {/if}
  </label>
</div>

<style>
  .ds-checkbox-container {
    display: inline-flex;
    align-items: center;
    vertical-align: middle;
  }

  .ds-checkbox-input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
  }

  .ds-checkbox-label {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    user-select: none;
    padding: 4px 0;
  }

  .checkbox-visual {
    width: 22px;
    height: 22px;
    border: 2px solid var(--ds-neutral-300, #E2E8F0);
    border-radius: 7px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    color: white;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  .check-icon {
    width: 14px;
    height: 14px;
    opacity: 0;
    transform: translateY(1px) scale(0.6);
    transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }

  /* Tono de la casilla marcada. El azul sigue siendo el de por defecto. */
  .ds-checkbox--info {
    --ds-checkbox-accent: var(--ds-info-500, #3399FF);
    --ds-checkbox-soft: var(--ds-info-300, #99CCFF);
    --ds-checkbox-glow: rgba(51, 153, 255, 0.25);
  }
  .ds-checkbox--success {
    --ds-checkbox-accent: var(--ds-success-500, #22C55E);
    --ds-checkbox-soft: var(--ds-success-300, #86EFAC);
    --ds-checkbox-glow: rgba(34, 197, 94, 0.25);
  }

  .ds-checkbox-input:checked + .ds-checkbox-label .checkbox-visual {
    background: var(--ds-checkbox-accent);
    border-color: var(--ds-checkbox-accent);
    box-shadow: 0 4px 10px var(--ds-checkbox-glow);
  }

  .ds-checkbox-input:checked + .ds-checkbox-label .check-icon {
    opacity: 1;
    transform: translateY(1px) scale(1);
  }

  .ds-checkbox-label:hover .checkbox-visual {
    border-color: var(--ds-checkbox-soft);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
  }

  .ds-checkbox-input:focus-visible + .ds-checkbox-label .checkbox-visual {
    outline: 2px solid var(--ds-checkbox-soft);
    outline-offset: 2px;
  }

  /* Deshabilitada: sin puntero ni hover, y atenuada. Una casilla ya marcada
     que no se puede desmarcar se sigue leyendo verde, solo apagada. */
  .ds-checkbox-container.is-disabled {
    opacity: 0.55;
  }
  .ds-checkbox-container.is-disabled .ds-checkbox-label {
    cursor: not-allowed;
  }
  .ds-checkbox-container.is-disabled .ds-checkbox-label:hover .checkbox-visual {
    transform: none;
    border-color: var(--ds-neutral-300, #E2E8F0);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  .ds-checkbox-container.is-disabled
    .ds-checkbox-input:checked
    + .ds-checkbox-label:hover
    .checkbox-visual {
    border-color: var(--ds-checkbox-accent);
  }

  .label-text {
    font-size: 14px;
    font-weight: 600;
    color: var(--ds-neutral-700, #1E293B);
    letter-spacing: -0.01em;
  }
</style>
