<script lang="ts">
  /**
   * Configuración del Proyecto de Emprendimiento.
   *
   * Hoy solo el formato del código, pero es el lugar donde van a caer las
   * reglas que el proceso todavía no tiene definidas: plazos, si hay que
   * cerrar una etapa para abrir la siguiente, qué exige cada actividad.
   *
   * El ejemplo de código lo calcula el backend y no esta pantalla: la regla
   * vive allá, y rearmarla acá sería tenerla en dos sitios que se pueden
   * desincronizar.
   */
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import { Badge, Button, Select, TextField } from '$lib/ds';
  import { auth } from '$lib/auth.svelte';
  import { branding } from '$lib/branding.svelte';
  import { configuration as cfg } from '$lib/configuration.svelte';

  let prefix = $state('');
  let includeYear = $state(true);
  let digits = $state(3);
  let saved = $state(false);

  let original = $state({ prefix: '', includeYear: true, digits: 3 });

  const dirty = $derived(
    prefix !== original.prefix ||
    includeYear !== original.includeYear ||
    digits !== original.digits,
  );
  const canEdit = $derived(!!auth.user?.is_superuser);

  // Vista previa local. Es la única regla duplicada del backend, y a propósito:
  // sin ella habría que ir al servidor con cada tecla para ver el efecto.
  const preview = $derived.by(() => {
    const year = new Date().getFullYear();
    const number = '1'.padStart(Math.max(1, Math.min(digits, 8)), '0');
    return includeYear ? `${prefix}-${year}-${number}` : `${prefix}-${number}`;
  });

  onMount(async () => {
    await cfg.load();
    if (cfg.data) {
      prefix = original.prefix = cfg.data.project_code_prefix;
      includeYear = original.includeYear = cfg.data.project_code_include_year;
      digits = original.digits = cfg.data.project_code_digits;
    }
  });

  function discard() {
    prefix = original.prefix;
    includeYear = original.includeYear;
    digits = original.digits;
    saved = false;
  }

  async function save() {
    saved = false;
    const ok = await cfg.save({
      project_code_prefix: prefix,
      project_code_include_year: includeYear,
      project_code_digits: digits,
    });
    if (ok) {
      original = { prefix, includeYear, digits };
      saved = true;
    }
  }
</script>

<svelte:head><title>Proyecto de Emprendimiento · {branding.data.name}</title></svelte:head>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <a class="crumb light" href="{base}/settings">CONFIGURACIÓN</a>
    <span class="sep">/</span>
    <span class="crumb dark">PROYECTO DE EMPRENDIMIENTO</span>
  </nav>

  <header class="head">
    <div>
      <h1 class="title">Proyecto de Emprendimiento</h1>
      <p class="sub">Cómo se comporta el módulo en {branding.data.name}.</p>
    </div>
    <div class="head-actions">
      {#if dirty}<Badge variant="warning" size="sm">Sin guardar</Badge>{/if}
      {#if saved && !dirty}<Badge variant="success" size="sm">Guardado</Badge>{/if}
    </div>
  </header>

  {#if !canEdit}
    <p class="notice">
      Solo un administrador puede cambiar esta configuración. Puedes verla, pero
      al guardar el servidor rechazará el cambio.
    </p>
  {/if}

  {#if cfg.errorMessage}
    <p class="error">{cfg.errorMessage}</p>
  {/if}

  {#if cfg.loading}
    <p class="muted">Cargando…</p>
  {:else}
    <section class="panel">
      <div class="panel-head">
        <h2>Código del proyecto</h2>
        <p>
          El identificador que se le pone a cada proyecto al crearlo. Lo lee la
          gente y termina en actas, así que una vez asignado no cambia.
        </p>
      </div>

      <div class="fields">
        <div class="field">
          <TextField
            label="Prefijo"
            bind:value={prefix}
            placeholder="PE"
          />
          <span class="hint">Mayúsculas, dígitos y guion.</span>
        </div>

        <div class="field">
          <Select
            label="Incluir el año"
            options={[
              { value: 'si', label: 'Sí' },
              { value: 'no', label: 'No' },
            ]}
            value={includeYear ? 'si' : 'no'}
            onchange={(v) => (includeYear = v === 'si')}
          />
          <span class="hint">Con año se reinicia la numeración cada enero.</span>
        </div>

        <div class="field">
          <Select
            label="Dígitos del número"
            options={[3, 4, 5, 6].map((n) => ({ value: String(n), label: String(n) }))}
            value={String(digits)}
            onchange={(v) => (digits = Number(v))}
          />
          <span class="hint">Cuántos proyectos por año esperas.</span>
        </div>
      </div>

      <div class="preview">
        <span class="preview-label">Así quedaría el próximo</span>
        <span class="preview-code">{preview}</span>
      </div>
    </section>

    <footer class="actions">
      <Button variant="outline" onclick={discard} disabled={!dirty || cfg.saving}>
        Descartar
      </Button>
      <Button
        variant="primary"
        loading={cfg.saving}
        disabled={!dirty || cfg.saving}
        onclick={save}
      >
        Guardar
      </Button>
    </footer>
  {/if}
</main>

<style>
  .page { max-width: 860px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; }
  .crumb.light { color: var(--ds-neutral-500, #94a3b8); text-decoration: none; }
  .crumb.light:hover { color: var(--ds-brand-500); }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }
  .sep { color: var(--ds-neutral-400, #cbd5e1); }

  .head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .title { margin: 0; font-size: 24px; font-weight: 800; color: var(--ds-neutral-800, #1e293b); }
  .sub { margin: 4px 0 0; font-size: 13px; color: var(--ds-neutral-500, #64748b); }
  .head-actions { display: flex; align-items: center; gap: 8px; }

  .panel {
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; padding: 24px;
    display: flex; flex-direction: column; gap: 22px;
  }
  .panel-head h2 { margin: 0; font-size: 15px; font-weight: 700; color: var(--ds-neutral-800, #1e293b); }
  .panel-head p { margin: 6px 0 0; font-size: 12.5px; color: var(--ds-neutral-500, #64748b); max-width: 62ch; }

  .fields { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 16px; }
  .field { display: flex; flex-direction: column; gap: 5px; }
  .hint { font-size: 11px; color: var(--ds-neutral-400, #94a3b8); }

  .preview {
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
    border-top: 1px dashed var(--ds-neutral-200, #e2e8f0); padding-top: 18px;
  }
  .preview-label {
    font-size: 11px; font-weight: 800; letter-spacing: 0.05em;
    text-transform: uppercase; color: var(--ds-neutral-400, #94a3b8);
  }
  .preview-code {
    font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700;
    color: var(--ds-brand-600); background: var(--ds-brand-100);
    padding: 6px 14px; border-radius: 8px;
  }

  .actions { display: flex; justify-content: flex-end; gap: 10px; }

  .muted { color: var(--ds-neutral-500, #64748b); font-size: 13px; }
  .notice, .error { margin: 0; padding: 10px 14px; border-radius: 8px; font-size: 13px; }
  .notice {
    background: var(--ds-warning-100, #FFF7E6); color: var(--ds-warning-700, #8a5a00);
    border: 1px solid var(--ds-warning-300, #FFE0A3);
  }
  .error {
    background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700);
    border: 1px solid var(--ds-error-300);
  }

  @media (max-width: 700px) { .fields { grid-template-columns: 1fr; } }
</style>
