<script lang="ts">
  /**
   * Identidad visual de la institución.
   *
   * Misma idea que `core-sv/src/routes/settings/branding` en el monorepo de
   * InnoTech: dos colores, su muestra, su código hex y una vista previa.
   *
   * Lo que hace distinto a esta pantalla de un formulario cualquiera es que
   * **el cambio se ve antes de guardar**: al mover un color se repintan los
   * tokens de toda la aplicación en vivo. Si el usuario se arrepiente, se
   * revierte a lo guardado.
   *
   * Solo administradores pueden guardar; lo valida el backend, no esta
   * pantalla. Acá el aviso es cortesía, no seguridad.
   */
  import { onMount } from 'svelte';
  import { Badge, Button, ProgressBar } from '$lib/ds';
  import { auth } from '$lib/auth.svelte';
  import { branding } from '$lib/branding.svelte';

  let primary = $state('#349AFE');
  let secondary = $state('#150089');
  let saved = $state(false);

  // Lo que está guardado, para saber si hay algo sin guardar y para el botón
  // de descartar.
  let originalPrimary = $state('#349AFE');
  let originalSecondary = $state('#150089');

  const dirty = $derived(primary !== originalPrimary || secondary !== originalSecondary);
  const canEdit = $derived(!!auth.user?.is_superuser);

  onMount(() => {
    primary = originalPrimary = branding.data.primary_color;
    secondary = originalSecondary = branding.data.secondary_color;

    // Al salir de la pantalla sin guardar, la aplicación no puede quedarse con
    // los colores de la vista previa.
    return () => branding.restore();
  });

  // Cada cambio de color repinta los tokens al instante.
  $effect(() => {
    branding.preview(primary, secondary);
  });

  function discard() {
    primary = originalPrimary;
    secondary = originalSecondary;
    saved = false;
  }

  async function save() {
    saved = false;
    if (await branding.save(primary, secondary)) {
      originalPrimary = primary;
      originalSecondary = secondary;
      saved = true;
    }
  }
</script>

<svelte:head><title>Identidad visual · {branding.data.name}</title></svelte:head>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <span class="crumb light">CONFIGURACIÓN</span>
    <span class="sep">/</span>
    <span class="crumb dark">IDENTIDAD VISUAL</span>
  </nav>

  <header class="head">
    <div>
      <h1 class="title">Identidad visual</h1>
      <p class="sub">
        Los colores de <strong>{branding.data.name}</strong>. Se aplican en toda
        la aplicación.
      </p>
    </div>
    <div class="head-actions">
      {#if dirty}<Badge variant="warning" size="sm">Sin guardar</Badge>{/if}
      {#if saved && !dirty}<Badge variant="success" size="sm">Guardado</Badge>{/if}
    </div>
  </header>

  {#if !canEdit}
    <p class="notice">
      Solo un administrador puede cambiar la identidad visual. Puedes probar
      colores acá, pero al guardar el servidor rechazará el cambio.
    </p>
  {/if}

  {#if branding.errorMessage}
    <p class="error">{branding.errorMessage}</p>
  {/if}

  <section class="panel">
    <div class="swatches">
      <div class="swatch">
        <div class="swatch-preview" style="background: {primary}">
          <input id="primary-color" type="color" bind:value={primary} />
        </div>
        <div class="swatch-info">
          <label for="primary-color" class="swatch-label">Color primario</label>
          <span class="hex">{primary.toUpperCase()}</span>
          <span class="swatch-hint">Botones, enlaces y estados activos.</span>
        </div>
      </div>

      <div class="swatch">
        <div class="swatch-preview" style="background: {secondary}">
          <input id="secondary-color" type="color" bind:value={secondary} />
        </div>
        <div class="swatch-info">
          <label for="secondary-color" class="swatch-label">Color secundario</label>
          <span class="hex">{secondary.toUpperCase()}</span>
          <span class="swatch-hint">Acentos y elementos de apoyo.</span>
        </div>
      </div>
    </div>

    <!-- Vista previa. Son componentes reales del design system, no dibujos:
         lo que se ve acá es literalmente lo que se verá en las pantallas. -->
    <div class="preview">
      <span class="preview-title">Vista previa</span>
      <div class="preview-row">
        <Button variant="primary" size="md">Botón primario</Button>
        <Button variant="outline" size="md">Secundario</Button>
        <Badge variant="primary" size="sm">Etiqueta</Badge>
      </div>
      <ProgressBar value={65} showValue />
    </div>
  </section>

  <footer class="actions">
    <Button variant="outline" onclick={discard} disabled={!dirty || branding.saving}>
      Descartar
    </Button>
    <Button
      variant="primary"
      loading={branding.saving}
      disabled={!dirty || branding.saving}
      onclick={save}
    >
      Guardar
    </Button>
  </footer>
</main>

<style>
  .page { max-width: 860px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; }
  .crumb.light { color: var(--ds-neutral-500, #94a3b8); }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }
  .sep { color: var(--ds-neutral-400, #cbd5e1); }

  .head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .title { margin: 0; font-size: 24px; font-weight: 800; color: var(--ds-neutral-800, #1e293b); }
  .sub { margin: 4px 0 0; font-size: 13px; color: var(--ds-neutral-500, #64748b); }
  .head-actions { display: flex; align-items: center; gap: 8px; }

  .panel {
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; padding: 24px;
    display: flex; flex-direction: column; gap: 28px;
  }

  .swatches { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }

  .swatch { display: flex; align-items: center; gap: 14px; }

  /* El `input type=color` va encima de la muestra y transparente: así se
     pincha el cuadro grande y no un control diminuto del navegador. */
  .swatch-preview {
    position: relative; width: 64px; height: 64px; border-radius: 12px;
    border: 1px solid var(--ds-neutral-200, #e2e8f0); flex-shrink: 0;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04);
  }
  .swatch-preview input[type='color'] {
    position: absolute; inset: 0; width: 100%; height: 100%;
    opacity: 0; cursor: pointer; border: 0; padding: 0; background: none;
  }

  .swatch-info { display: flex; flex-direction: column; min-width: 0; }
  .swatch-label { font-size: 13px; font-weight: 700; color: var(--ds-neutral-700, #334155); cursor: pointer; }
  .hex {
    font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600;
    color: var(--ds-neutral-500, #64748b); margin-top: 2px;
  }
  .swatch-hint { font-size: 11px; color: var(--ds-neutral-400, #94a3b8); margin-top: 4px; }

  .preview {
    border-top: 1px dashed var(--ds-neutral-200, #e2e8f0); padding-top: 20px;
    display: flex; flex-direction: column; gap: 14px;
  }
  .preview-title {
    font-size: 11px; font-weight: 800; letter-spacing: 0.05em;
    text-transform: uppercase; color: var(--ds-neutral-400, #94a3b8);
  }
  .preview-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }

  .actions { display: flex; justify-content: flex-end; gap: 10px; }

  .notice, .error {
    margin: 0; padding: 10px 14px; border-radius: 8px; font-size: 13px;
  }
  .notice {
    background: var(--ds-warning-100, #FFF7E6); color: var(--ds-warning-700, #8a5a00);
    border: 1px solid var(--ds-warning-300, #FFE0A3);
  }
  .error {
    background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700);
    border: 1px solid var(--ds-error-300);
  }

  @media (max-width: 640px) {
    .swatches { grid-template-columns: 1fr; }
  }
</style>
