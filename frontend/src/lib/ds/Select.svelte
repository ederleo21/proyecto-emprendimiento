<!-- Copia de `@innotech/ui-svelte/components/inputs/Select.svelte` del monorepo
     de InnoTech.

     Dos cambios, ambos mecánicos: la ruta del `Icon` —acá viven en la misma
     carpeta— y tres nombres de icono que este proyecto tiene con otro nombre
     (`design-system/chevron-down` → `arrows/chevron-down`, y así).

     Reemplaza al `Select` que estaba hecho acá, que era un desplegable nativo
     del navegador. Este es propio: se puede buscar dentro, se anima al abrir y
     se ve igual en todos los navegadores. -->
<script lang="ts">
  import Icon from "./Icon.svelte";
  import type { Snippet } from "svelte";
  import { onMount, tick, untrack } from "svelte";

  interface Option {
    value: any;
    label: string;
    disabled?: boolean;
    searchTerms?: string;
    /** Código corto mostrado como chip antes del label (opcional). */
    code?: string;
  }

  interface Props {
    label?: string;
    placeholder?: string;
    value?: any;
    options?: Option[];
    status?: "Default" | "Focused" | "Success" | "Warning" | "Error";
    message?: string;
    size?: "sm" | "md" | "lg";
    prefix?: Snippet;
    suffix?: Snippet;
    labelClass?: string;
    class?: string;
    /** Si true, muestra un input de busqueda dentro del dropdown. */
    searchable?: boolean;
    disabled?: boolean;
    required?: boolean;
    name?: string;
    /** Callbacks opcionales (alternativa a bind:value). */
    onchange?: (value: any) => void;
    onselect?: (value: any) => void;
    /** Renderiza el dropdown con position:fixed para escapar contenedores con overflow:auto (ej. modales). */
    portal?: boolean;
    /** Fuerza que el menú abra SIEMPRE hacia abajo (desactiva el flip automático hacia arriba). */
    preferDown?: boolean;
    isOpen?: boolean;
    [key: string]: any;
  }

  let {
    label = "",
    placeholder = "Seleccionar...",
    value = $bindable(""),
    options = [],
    status = "Default",
    message = "",
    size = "md",
    prefix,
    suffix,
    labelClass = "",
    id = `sel-${Math.random().toString(36).substring(2, 9)}`,
    class: customClass = "",
    searchable = false,
    disabled = false,
    required = false,
    name,
    onchange,
    onselect,
    portal = false,
    preferDown = false,
    isOpen = $bindable(false),
    ...rest
  }: Props = $props();

  let menuStyle = $state("");

  const statusColors: Record<string, string> = {
    Default: "text-ds-neutral-500",
    Focused: "text-ds-info-500",
    Success: "text-ds-success-500",
    Warning: "text-ds-warning-500",
    Error: "text-ds-error-500",
  };

  const statusIcons: Record<string, string> = {
    Success: "design-system/check",
    Warning: "design-system/alert",
    Error: "design-system/error",
  };

  const iconSizeMap: Record<string, string> = { sm: "xs", md: "sm", lg: "md" };
  const derivedIconSize = $derived(iconSizeMap[size] || "sm");

  let searchTerm = $state("");
  let highlightedIndex = $state(-1);
  let wrapperEl = $state<HTMLDivElement | null>(null);
  let triggerEl = $state<HTMLButtonElement | null>(null);
  let menuEl = $state<HTMLDivElement | null>(null);
  let searchInputEl = $state<HTMLInputElement | null>(null);
  /** Si TRUE, el menu se abre hacia arriba (cuando no cabe debajo del trigger). */
  let openUpward = $state(false);

  const activeStatus = $derived(isOpen ? "Focused" : status);

  const filteredOptions = $derived(
    searchable && searchTerm.trim()
      ? options.filter((o) => {
          const term = searchTerm.trim().toLowerCase();
          const labelMatch = o.label.toLowerCase().includes(term);
          const codeMatch = o.code ? o.code.toLowerCase().includes(term) : false;
          const searchTermsMatch = o.searchTerms ? o.searchTerms.toLowerCase().includes(term) : false;
          return labelMatch || codeMatch || searchTermsMatch;
        })
      : options,
  );

  const selectedOption = $derived(options.find((o) => o.value === value));

  /** Decide si abrir hacia arriba antes de mostrar el menu.
   *  En modo portal usa position:fixed calculado desde getBoundingClientRect
   *  para escapar contenedores con overflow:auto (ej. ds-modal-body). */
  // Portal automático dentro de modales: .ds-modal-body (overflow + scroll
  // iOS) crea un stacking context que atrapa el z-index del menú absoluto y
  // el footer del modal pinta encima. En ese caso el menú usa position:fixed.
  let effectivePortal = $state(false);

  function computeOpenDirection() {
    if (!triggerEl) return;
    effectivePortal = portal || !!triggerEl.closest('.ds-modal-body');
    const rect = triggerEl.getBoundingClientRect();
    const viewportH = window.innerHeight;
    const viewportW = window.innerWidth;
    const spaceBelow = viewportH - rect.bottom;
    const spaceAbove = rect.top;
    const MENU_MAX = 340;
    // preferDown desactiva el flip hacia arriba: abre siempre hacia abajo.
    openUpward = !preferDown && spaceBelow < MENU_MAX && spaceAbove > spaceBelow;

    if (effectivePortal) {
      // Ancho mínimo 280px para evitar cortar labels largos en triggers pequeños.
      const menuWidth = Math.max(rect.width, 280);
      const leftClamped = Math.max(8, Math.min(rect.left, viewportW - menuWidth - 8));
      if (openUpward) {
        menuStyle = `position:fixed;bottom:${viewportH - rect.top + 6}px;top:auto;left:${leftClamped}px;width:${menuWidth}px;`;
      } else {
        menuStyle = `position:fixed;top:${rect.bottom + 6}px;bottom:auto;left:${leftClamped}px;width:${menuWidth}px;`;
      }
    }
  }

  $effect(() => {
    const open = isOpen;
    untrack(() => {
      if (open) {
        computeOpenDirection();
        searchTerm = "";
        const selIdx = filteredOptions.findIndex((o) => o.value === value);
        highlightedIndex = selIdx >= 0 ? selIdx : 0;
        tick().then(() => {
          if (searchable && searchInputEl) searchInputEl.focus();
          const selEl = menuEl?.querySelector(
            ".ds-select-option.is-selected",
          ) as HTMLElement | null;
          selEl?.scrollIntoView({ block: "nearest" });
        });
      } else {
        searchTerm = "";
        highlightedIndex = -1;
      }
    });
  });

  function toggle() {
    if (disabled) return;
    isOpen = !isOpen;
  }

  function close() {
    isOpen = false;
  }

  function selectOption(opt: Option) {
    if (opt.disabled) return;
    value = opt.value;
    onchange?.(opt.value);
    onselect?.(opt.value);
    close();
    triggerEl?.focus();
  }

  function handleClickOutside(e: MouseEvent) {
    if (!wrapperEl) return;
    const target = e.target as Node | null;
    if (target && !wrapperEl.contains(target)) close();
  }

  function handleTriggerKey(e: KeyboardEvent) {
    if (disabled) return;
    if (!isOpen) {
      if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
        e.preventDefault();
        toggle();
      }
      return;
    }
    handleMenuKey(e);
  }

  function handleMenuKey(e: KeyboardEvent) {
    if (e.key === "Escape") {
      e.preventDefault();
      close();
      triggerEl?.focus();
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      moveHighlight(1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      moveHighlight(-1);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (highlightedIndex >= 0 && filteredOptions[highlightedIndex]) {
        selectOption(filteredOptions[highlightedIndex]);
      }
    } else if (e.key === "Tab") {
      close();
    }
  }

  function moveHighlight(delta: number) {
    const len = filteredOptions.length;
    if (len === 0) return;
    let i = highlightedIndex + delta;
    while (i >= 0 && i < len && filteredOptions[i]?.disabled) i += delta;
    if (i < 0) i = 0;
    if (i >= len) i = len - 1;
    highlightedIndex = i;
  }

  onMount(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  });

  $effect(() => {
    if (!isOpen || !effectivePortal) return;
    const onScroll = (e: Event) => {
      if (menuEl && e.target instanceof Node && menuEl.contains(e.target))
        return;
      close();
    };
    const onResize = () => computeOpenDirection();
    window.addEventListener("scroll", onScroll, true);
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("scroll", onScroll, true);
      window.removeEventListener("resize", onResize);
    };
  });
</script>

<div
  class="ds-input-container ds-select-container {customClass}"
  bind:this={wrapperEl}
>
  {#if label}
    <label class="ds-field-label BodyM {labelClass}" for={id}>{label}</label>
  {/if}

  <div class="ds-select-anchor">
    <div
      class="ds-field {activeStatus.toLowerCase()} {size}
      {prefix ? 'has-prefix' : ''}
      {suffix ? 'has-suffix' : ''}
      ds-select-wrapper"
      class:is-open={isOpen}
      class:is-disabled={disabled}
    >
      {#if prefix}
        <div class="ds-prefix">{@render prefix()}</div>
      {/if}

      <button
        type="button"
        {id}
        class="ds-input ds-select-trigger"
        onclick={toggle}
        onkeydown={handleTriggerKey}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-disabled={disabled}
        {disabled}
        bind:this={triggerEl}
        {...rest}
      >
        <span class="ds-select-value" class:is-placeholder={!selectedOption}>
          {#if selectedOption?.code}<span class="ds-select-code">{selectedOption.code}</span>{/if}
          {selectedOption?.label ?? placeholder}
        </span>
      </button>

      <div class="ds-suffix ds-select-chevron">
        {#if suffix}{@render suffix()}{/if}
        <Icon
          name="arrows/chevron-down"
          size={derivedIconSize}
          class={`!text-ds-neutral-400 chev ${isOpen ? "chev--open" : ""}`}
        />
      </div>
    </div>

    <!-- Menu dropdown fuera de .ds-field para escapar su overflow:hidden. -->
    {#if isOpen}
      <div
        class="ds-select-menu"
        class:is-up={openUpward}
        style={effectivePortal ? menuStyle : ""}
        role="listbox"
        tabindex="-1"
        bind:this={menuEl}
        onkeydown={handleMenuKey}
      >
        {#if searchable}
          <div class="ds-select-search">
            <Icon
              name="system/search"
              size="xs"
              class="!text-ds-neutral-400"
            />
            <input
              type="text"
              bind:value={searchTerm}
              bind:this={searchInputEl}
              placeholder="Buscar..."
              onkeydown={handleMenuKey}
            />
          </div>
        {/if}

        <div class="ds-select-options">
          {#if filteredOptions.length === 0}
            <div class="ds-select-empty">Sin resultados</div>
          {:else}
            {#each filteredOptions as opt, i}
              <button
                type="button"
                role="option"
                class="ds-select-option"
                class:is-highlighted={highlightedIndex === i}
                class:is-selected={value === opt.value}
                class:is-disabled={opt.disabled}
                aria-selected={value === opt.value}
                aria-disabled={opt.disabled}
                title={opt.label}
                onclick={() => selectOption(opt)}
                onmouseenter={() => (highlightedIndex = i)}
              >
                <span class="ds-select-option-label">
                  {#if opt.code}<span class="ds-select-code">{opt.code}</span>{/if}
                  {opt.label}
                </span>
                <Icon
                  name="arrows/chevron-right"
                  size="xs"
                  class="!text-ds-neutral-400 ds-select-option-arrow"
                />
              </button>
            {/each}
          {/if}
        </div>
      </div>
    {/if}
  </div>

  {#if name}
    <input type="hidden" {name} {value} />
  {/if}

  {#if message}
    <div class="ds-message {status.toLowerCase()}">
      {#if statusIcons[status]}
        <Icon
          name={statusIcons[status]}
          size="sm"
          class="!{statusColors[status]}"
        />
      {/if}
      <span class="CaptionSM {statusColors[status]}">{message}</span>
    </div>
  {/if}
</div>

<style>
  /* Con el menú abierto, el contenedor sube su stacking para que el dropdown
     pinte por ENCIMA de hermanos posteriores (footer del modal, cards, etc.).
     Mismo patrón que DsDatePicker. */
  .ds-select-container {
    position: relative;
    z-index: 1;
  }
  .ds-select-container:has(.ds-select-menu) {
    z-index: 1000;
  }

  /* Anchor intermedio sin overflow para que el dropdown sobresalga de .ds-field. */
  .ds-select-anchor {
    position: relative;
    width: 100%;
  }

  /* ── Trigger ────────────────────────────────────────────── */
  .ds-select-wrapper {
    cursor: pointer;
  }
  .ds-select-wrapper.is-disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
  .ds-select-wrapper.is-open {
    border-color: var(--ds-info-500);
    box-shadow: 0 0 0 3px rgba(51, 153, 255, 0.12);
  }

  .ds-select-trigger {
    background: transparent;
    border: none;
    outline: none;
    text-align: left;
    cursor: inherit;
    padding: 0 16px;
    display: flex;
    align-items: center;
    width: 100%;
    height: 100%;
    font-family: inherit;
    color: var(--ds-neutral-700);
  }

  .ds-select-value {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .ds-select-value.is-placeholder {
    color: var(--ds-neutral-400);
  }
  /* Estándar UBE: las opciones y el valor seleccionado (datos) se muestran en
     MAYÚSCULAS. No aplica al placeholder ni cambia el value real. Va aquí (no
     por CSS externo) porque el dropdown se renderiza con portal. */
  .ds-select-value:not(.is-placeholder),
  .ds-select-option-label {
    text-transform: uppercase;
  }

  .ds-select-chevron {
    position: absolute;
    right: 12px;
    pointer-events: none;
  }
  :global(.ds-select-chevron .chev) {
    transition: transform 0.18s ease;
  }
  :global(.ds-select-chevron .chev--open) {
    transform: rotate(180deg);
  }

  /* ── Menu dropdown ──────────────────────────────────────── */
  .ds-select-menu {
    position: absolute;
    top: calc(100% + 6px);
    bottom: auto;
    left: 0;
    right: 0;
    z-index: 9999;
    background: white;
    border: 1px solid var(--ds-neutral-200, var(--ds-neutral-300));
    border-radius: var(--ds-radius-md, 10px);
    box-shadow: var(--ds-shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.12));
    max-height: 320px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    animation: dsSelectOpen 0.12s ease;
  }

  /* Auto-flip: si el trigger no tiene espacio debajo, abrimos arriba. */
  .ds-select-menu.is-up {
    top: auto;
    bottom: calc(100% + 6px);
    animation: dsSelectOpenUp 0.12s ease;
  }

  @keyframes dsSelectOpen {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  @keyframes dsSelectOpenUp {
    from {
      opacity: 0;
      transform: translateY(4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .ds-select-search {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    border-bottom: 1px solid var(--ds-neutral-100);
    background: white;
  }
  .ds-select-search input {
    border: none;
    outline: none;
    flex: 1;
    font-size: 13px;
    color: var(--ds-neutral-700);
    background: transparent;
    font-family: inherit;
  }
  .ds-select-search input::placeholder {
    color: var(--ds-neutral-400);
  }

  .ds-select-options {
    overflow-y: auto;
    padding: 4px 0;
    flex: 1;
  }

  .ds-select-empty {
    padding: 16px;
    text-align: center;
    color: var(--ds-neutral-500);
    font-size: 13px;
  }

  .ds-select-option {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
    width: 100%;
    padding: 10px 14px;
    background: white;
    border: none;
    text-align: left;
    cursor: pointer;
    font-size: 14px;
    color: var(--ds-neutral-700);
    font-family: inherit;
    transition: background 0.1s ease, color 0.1s ease;
  }
  .ds-select-option:hover:not(.is-disabled),
  .ds-select-option.is-highlighted:not(.is-disabled) {
    background: var(--ds-info-100);
    color: var(--ds-info-700);
  }
  .ds-select-option.is-selected {
    background: var(--ds-info-100);
    color: var(--ds-info-700);
    font-weight: 600;
  }
  .ds-select-option.is-disabled {
    color: var(--ds-neutral-400);
    cursor: not-allowed;
    background: transparent;
  }
  :global(.ds-select-option-arrow) {
    opacity: 0;
    transition: opacity 0.12s ease;
  }
  .ds-select-option:hover :global(.ds-select-option-arrow),
  .ds-select-option.is-highlighted :global(.ds-select-option-arrow) {
    opacity: 1;
  }

  .ds-select-option-label {
    flex: 1;
    /* Labels largos hacen wrap en vez de mostrar "...". */
    white-space: normal;
    overflow-wrap: anywhere;
    line-height: 1.4;
    min-width: 0;
  }

  /* Código antes del label: solo negrita, sin fondo (opt-in vía Option.code). */
  .ds-select-code {
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    letter-spacing: 0.03em;
    margin-right: 6px;
  }

  .ds-select-options::-webkit-scrollbar {
    width: 6px;
  }
  .ds-select-options::-webkit-scrollbar-thumb {
    background: var(--ds-neutral-300);
    border-radius: 3px;
  }
</style>
