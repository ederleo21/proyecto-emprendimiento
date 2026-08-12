<!-- Copia de `@innotech/ui-svelte/components/Switch.svelte` del monorepo de InnoTech.
     Sin cambios. Trae sus propias transiciones. -->
<script lang="ts">
  export let checked = false;
  export let label = "";
  export let description = "";
  export let disabled = false;
</script>

<div class="admin-switch" class:is-disabled={disabled}>
  <div class="switch-info">
    <span class="switch-label">{label}</span>
    {#if description}
      <span class="switch-description">{description}</span>
    {/if}
  </div>
  <label class="switch-control" class:is-disabled={disabled}>
    <input type="checkbox" bind:checked {disabled} />
    <span class="slider"></span>
  </label>
</div>

<style>
  .admin-switch {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: var(--surface-alt);
    border: 1px solid var(--line);
    border-radius: 20px;
    transition: all 0.2s;
  }
  .admin-switch:focus-within {
    border-color: var(--brand);
    background: var(--surface);
    box-shadow: 0 4px 12px rgba(52, 154, 254, 0.08);
  }
  .admin-switch.is-disabled { opacity: 0.55; }
  .admin-switch.is-disabled:focus-within {
    border-color: var(--line);
    background: var(--surface-alt);
    box-shadow: none;
  }
  .switch-info { display: flex; flex-direction: column; gap: 2px; }
  .switch-label { font-size: 11px; font-weight: 850; color: var(--brand-strong); text-transform: uppercase; letter-spacing: 0.05em; }
  .switch-description { font-size: 12px; font-weight: 500; color: var(--ink-500); }

  .switch-control {
    position: relative;
    display: inline-block;
    width: 48px;
    height: 26px;
    cursor: pointer;
  }
  .switch-control.is-disabled { cursor: not-allowed; }
  .switch-control input { opacity: 0; width: 0; height: 0; }
  .switch-control input:disabled { cursor: not-allowed; }
  .slider {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: var(--line);
    transition: .3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 34px;
  }
  .slider:before {
    position: absolute;
    content: "";
    height: 20px;
    width: 20px;
    left: 3px;
    bottom: 3px;
    background-color: var(--surface);
    transition: .3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  input:checked + .slider { background-color: var(--brand-strong); }
  input:checked + .slider:before { transform: translateX(22px); }
  input:disabled + .slider { cursor: not-allowed; }
</style>
