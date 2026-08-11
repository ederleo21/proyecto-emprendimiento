<script lang="ts">
  /* Campo de texto.
   *
   * Firma alineada con `@innotech/ui-svelte/TextField`: `label`, `value`
   * bindable, `type`, `placeholder`, `size`, `oninput`.
   */
  interface Props {
    label?: string;
    value?: string | number;
    type?: 'text' | 'number' | 'email' | 'password' | 'date';
    placeholder?: string;
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    error?: string;
    rows?: number;
    /** Si viene, se pinta un `textarea` en vez de un `input`. */
    multiline?: boolean;
    class?: string;
    oninput?: (value: any) => void;
    [key: string]: any;
  }

  let {
    label = '',
    value = $bindable(''),
    type = 'text',
    placeholder = '',
    size = 'md',
    disabled = false,
    error = '',
    rows = 3,
    multiline = false,
    class: customClass = '',
    oninput,
    ...rest
  }: Props = $props();

  function handle(e: Event) {
    const target = e.target as HTMLInputElement | HTMLTextAreaElement;
    value = target.value;
    oninput?.(target.value);
  }
</script>

<div class="ds-field {customClass}">
  {#if label}<label class="ds-field-label">{label}</label>{/if}
  {#if multiline}
    <textarea
      class="ds-field-input ds-field-{size}"
      class:has-error={!!error}
      {placeholder} {disabled} {rows} {value}
      oninput={handle}
      {...rest}
    ></textarea>
  {:else}
    <input
      class="ds-field-input ds-field-{size}"
      class:has-error={!!error}
      {type} {placeholder} {disabled} {value}
      oninput={handle}
      {...rest}
    />
  {/if}
  {#if error}<span class="ds-field-error">{error}</span>{/if}
</div>

<style>
  .ds-field { display: flex; flex-direction: column; gap: 6px; }
  .ds-field-label {
    font-size: 13px; font-weight: 600; color: var(--ds-neutral-600, #475569);
  }
  .ds-field-input {
    width: 100%; box-sizing: border-box; font-family: inherit;
    border: 1px solid var(--ds-neutral-300, #e2e8f0); border-radius: 8px;
    background: #fff; color: var(--ds-neutral-800, #1e293b);
    transition: border-color 0.18s, box-shadow 0.18s;
  }
  .ds-field-input::placeholder { color: var(--ds-neutral-400, #94a3b8); }
  .ds-field-input:focus {
    outline: none; border-color: var(--ds-brand-500);
    box-shadow: 0 0 0 3px var(--ds-brand-100);
  }
  .ds-field-input:disabled { background: var(--ds-neutral-100, #f1f5f9); cursor: not-allowed; }
  .has-error { border-color: var(--ds-error-500); }

  .ds-field-sm { padding: 6px 10px; font-size: 12px; }
  .ds-field-md { padding: 9px 12px; font-size: 13px; }
  .ds-field-lg { padding: 12px 14px; font-size: 15px; }

  .ds-field-error { font-size: 12px; color: var(--ds-error-600); }
  textarea.ds-field-input { resize: vertical; min-height: 70px; line-height: 1.5; }
</style>
