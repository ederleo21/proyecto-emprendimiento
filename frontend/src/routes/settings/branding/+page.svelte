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
  import { Badge, Button, ProgressBar, TextField } from '$lib/ds';
  import { auth } from '$lib/auth.svelte';
  import { branding } from '$lib/branding.svelte';

  let name = $state('');
  let subtitle = $state('');
  let primary = $state('#349AFE');
  let secondary = $state('#150089');
  let saved = $state(false);

  // Lo que está guardado, para saber si hay algo pendiente y para descartar.
  let original = $state({ name: '', subtitle: '', primary: '', secondary: '' });

  let fileInput = $state<HTMLInputElement | null>(null);

  const dirty = $derived(
    name !== original.name ||
    subtitle !== original.subtitle ||
    primary !== original.primary ||
    secondary !== original.secondary,
  );
  const canEdit = $derived(!!auth.user?.is_superuser);

  onMount(() => {
    sync();
    // Al salir de la pantalla sin guardar, la aplicación no puede quedarse con
    // los colores de la vista previa.
    return () => branding.restore();
  });

  function sync() {
    name = branding.data.name;
    subtitle = branding.data.subtitle;
    primary = branding.data.primary_color;
    secondary = branding.data.secondary_color;
    original = { name, subtitle, primary, secondary };
  }

  // Cada cambio de color repinta los tokens al instante.
  $effect(() => {
    branding.preview(primary, secondary);
  });

  function discard() {
    name = original.name;
    subtitle = original.subtitle;
    primary = original.primary;
    secondary = original.secondary;
    saved = false;
  }

  async function save() {
    saved = false;
    const ok = await branding.save({
      name,
      subtitle,
      primary_color: primary,
      secondary_color: secondary,
    });
    if (ok) {
      original = { name, subtitle, primary, secondary };
      saved = true;
    }
  }

  async function onFilePicked(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    await branding.uploadLogo(file);
    // Se limpia para poder volver a elegir el mismo archivo si hizo falta.
    input.value = '';
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
    <div class="panel-head">
      <h2>Nombre y logotipo</h2>
      <p>Lo que se ve en la cabecera de todas las pantallas.</p>
    </div>

    <div class="identity">
      <div class="logo-box">
        {#if branding.data.logo_url}
          <img src={branding.data.logo_url} alt="Logotipo de {branding.data.name}" />
        {:else}
          <span class="logo-initial">{name.charAt(0) || '·'}</span>
        {/if}
      </div>

      <div class="logo-actions">
        <span class="logo-title">Logotipo</span>
        <span class="logo-hint">PNG, JPG, SVG o WEBP. Hasta 2 MB.</span>
        <div class="logo-buttons">
          <Button variant="outline" size="sm" disabled={branding.saving}
                  onclick={() => fileInput?.click()}>
            {branding.data.logo_url ? 'Reemplazar' : 'Subir'}
          </Button>
          {#if branding.data.logo_url}
            <Button variant="outline" size="sm" disabled={branding.saving}
                    onclick={() => branding.removeLogo()}>
              Quitar
            </Button>
          {/if}
        </div>
        <input
          bind:this={fileInput}
          type="file"
          accept=".png,.jpg,.jpeg,.svg,.webp"
          onchange={onFilePicked}
          hidden
        />
      </div>
    </div>

    <div class="texts">
      <div class="field">
        <TextField label="Nombre de la institución" bind:value={name} />
        <span class="hint">
          Si se conecta el IAM de InnoTech, la próxima sincronización lo
          reemplazará por el que tenga allá.
        </span>
      </div>
      <div class="field">
        <TextField label="Subtítulo" bind:value={subtitle}
                   placeholder="Vinculación con la Sociedad" />
        <span class="hint">La línea pequeña debajo del nombre.</span>
      </div>
    </div>
  </section>

  <section class="panel">
    <div class="panel-head">
      <h2>Colores</h2>
      <p>Se aplican en toda la aplicación apenas los mueves.</p>
    </div>

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
    display: flex; flex-direction: column; gap: 24px;
  }
  .panel-head h2 { margin: 0; font-size: 15px; font-weight: 700; color: var(--ds-neutral-800, #1e293b); }
  .panel-head p { margin: 6px 0 0; font-size: 12.5px; color: var(--ds-neutral-500, #64748b); }

  /* Nombre y logotipo */
  .identity { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }

  .logo-box {
    width: 96px; height: 96px; flex-shrink: 0;
    border: 1px dashed var(--ds-neutral-300, #cbd5e1); border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; background: var(--ds-neutral-100, #f8fafc);
  }
  .logo-box img { max-width: 100%; max-height: 100%; object-fit: contain; }
  .logo-initial {
    font-size: 34px; font-weight: 800;
    color: var(--ds-brand-500);
  }

  .logo-actions { display: flex; flex-direction: column; gap: 4px; }
  .logo-title { font-size: 13px; font-weight: 700; color: var(--ds-neutral-700, #334155); }
  .logo-hint { font-size: 11px; color: var(--ds-neutral-400, #94a3b8); }
  .logo-buttons { display: flex; gap: 8px; margin-top: 8px; }

  .texts { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .field { display: flex; flex-direction: column; gap: 5px; }
  .hint { font-size: 11px; color: var(--ds-neutral-400, #94a3b8); line-height: 1.45; }

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
    .swatches, .texts { grid-template-columns: 1fr; }
  }
</style>
