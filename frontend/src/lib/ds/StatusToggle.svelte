<!-- Copia de `@innotech/ui-svelte/components/StatusToggle.svelte` del monorepo
     de InnoTech. Sin cambios. Se usa este y no `Switch` porque avisa cuándo lo
     tocan (`onToggle`); el otro solo enlaza su propio estado. -->
<script lang="ts">
  /**
   * Componente StatusToggle Genérico (Svelte 5)
   * Permite definir colores personalizados para estados mediante props.
   */
  
  interface Props {
    isActive?: boolean;
    activeLabel?: string;
    inactiveLabel?: string;
    disabled?: boolean;
    activeColor?: string;
    inactiveColor?: string;
    disabledColor?: string;
    thumbColor?: string;
    activeTextColor?: string;
    inactiveTextColor?: string;
    onToggle?: (newState: boolean) => void;
  }

  let {
    isActive = $bindable(false),
    activeLabel = "Activo",
    inactiveLabel = "Inactivo",
    disabled = false,
    activeColor = "var(--ds-success-500)",
    inactiveColor = "var(--ds-neutral-300)",
    disabledColor = "var(--ds-neutral-100)",
    thumbColor = "var(--surface)",
    activeTextColor = "",
    inactiveTextColor = "var(--ds-neutral-500)",
    onToggle
  }: Props = $props();

  function toggle() {
    if (disabled) return;
    isActive = !isActive;
    if (onToggle) onToggle(isActive);
  }

  // Derived colors
  const currentActiveTextColor = $derived(activeTextColor || activeColor);
</script>

<button 
  class="status-toggle" 
  onclick={toggle} 
  {disabled} 
  class:is-disabled={disabled}
  style:--st-active-color={activeColor}
  style:--st-inactive-color={inactiveColor}
  style:--st-disabled-color={disabledColor}
  style:--st-thumb-color={thumbColor}
  style:--st-active-text={currentActiveTextColor}
  style:--st-inactive-text={inactiveTextColor}
>
  <div class="toggle-track" class:active={isActive}>
    <div class="toggle-thumb" class:active={isActive}></div>
  </div>
  <span class="status-text" class:active={isActive}>
    {isActive ? activeLabel : inactiveLabel}
  </span>
</button>

<style>
  .status-toggle {
    display: flex;
    align-items: center;
    gap: 12px;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 8px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    outline: none;
    user-select: none;
  }

  .status-toggle:hover:not(.is-disabled) {
    background: var(--ds-neutral-50, rgba(0,0,0,0.02));
  }

  .status-toggle.is-disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  .toggle-track {
    width: 36px;
    height: 20px;
    background: var(--st-inactive-color);
    border-radius: 100px;
    position: relative;
    transition: background-color 0.3s ease;
    flex-shrink: 0;
  }

  .toggle-track.active {
    background: var(--st-active-color);
  }

  .status-toggle.is-disabled .toggle-track {
    background: var(--st-disabled-color);
    border: 1px solid var(--ds-neutral-200);
  }

  .toggle-thumb {
    width: 14px;
    height: 14px;
    background: var(--st-thumb-color);
    border-radius: 50%;
    position: absolute;
    top: 3px;
    left: 3px;
    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: var(--ds-shadow-sm, 0 1px 2px rgba(0,0,0,0.1));
  }

  .toggle-thumb.active {
    transform: translateX(16px);
  }

  .status-text {
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--st-inactive-text);
    transition: color 0.3s ease;
  }

  .status-text.active {
    color: var(--st-active-text);
  }

  .status-toggle.is-disabled .status-text {
    color: var(--ds-neutral-400);
  }
</style>
