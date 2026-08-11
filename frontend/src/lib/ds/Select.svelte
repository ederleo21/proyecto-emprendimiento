<script lang="ts">
  /* Desplegable.
   *
   * Firma alineada con `@innotech/ui-svelte/Select`: `label`, `options`,
   * `value` bindable, `onchange`, `placeholder`, `size`.
   *
   * El de InnoTech además admite `searchable` y `portal`; acá se usa un
   * `<select>` nativo porque las pantallas de hoy no lo necesitan. Si hiciera
   * falta se reemplaza sin tocar quien lo usa: las props ya coinciden.
   */
  interface Option {
    value: string;
    label: string;
  }

  interface Props {
    label?: string;
    options?: Option[];
    value?: string;
    placeholder?: string;
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    class?: string;
    onchange?: (value: string) => void;
    [key: string]: any;
  }

  let {
    label = '',
    options = [],
    value = $bindable(''),
    placeholder = '',
    size = 'md',
    disabled = false,
    class: customClass = '',
    onchange,
    ...rest
  }: Props = $props();

  function handle(e: Event) {
    const target = e.target as HTMLSelectElement;
    value = target.value;
    onchange?.(target.value);
  }
</script>

<div class="ds-select {customClass}">
  {#if label}<label class="ds-select-label">{label}</label>{/if}
  <div class="ds-select-wrap">
    <select
      class="ds-select-input ds-select-{size}"
      {disabled} {value}
      onchange={handle}
      {...rest}
    >
      {#if placeholder}<option value="">{placeholder}</option>{/if}
      {#each options as opt (opt.value)}
        <option value={opt.value}>{opt.label}</option>
      {/each}
    </select>
    <svg class="ds-select-chevron" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="2.2" aria-hidden="true">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  </div>
</div>

<style>
  .ds-select { display: flex; flex-direction: column; gap: 6px; }
  .ds-select-label {
    font-size: 13px; font-weight: 600; color: var(--ds-neutral-600, #475569);
  }
  .ds-select-wrap { position: relative; display: flex; }
  .ds-select-input {
    width: 100%; box-sizing: border-box; font-family: inherit;
    appearance: none; -webkit-appearance: none;
    border: 1px solid var(--ds-neutral-300, #e2e8f0); border-radius: 8px;
    background: #fff; color: var(--ds-neutral-800, #1e293b);
    padding-right: 34px; cursor: pointer;
    transition: border-color 0.18s, box-shadow 0.18s;
  }
  .ds-select-input:focus {
    outline: none; border-color: var(--ds-brand-500);
    box-shadow: 0 0 0 3px var(--ds-brand-100);
  }
  .ds-select-input:disabled { background: var(--ds-neutral-100, #f1f5f9); cursor: not-allowed; }

  .ds-select-sm { padding: 6px 10px; font-size: 12px; }
  .ds-select-md { padding: 9px 12px; font-size: 13px; }
  .ds-select-lg { padding: 12px 14px; font-size: 15px; }

  .ds-select-chevron {
    position: absolute; right: 11px; top: 50%; transform: translateY(-50%);
    width: 15px; height: 15px; pointer-events: none;
    color: var(--ds-neutral-500, #64748b);
  }
</style>
