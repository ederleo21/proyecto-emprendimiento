<script lang="ts">
  /**
   * Los permisos de un rol.
   *
   * Una fila por módulo con sus casillas, como cualquier gestor de permisos.
   * El catálogo viene del backend y es de solo lectura: un permiso existe
   * porque hay código que lo comprueba, así que no se inventan desde acá.
   *
   * El interruptor del módulo es un atajo —marca o desmarca sus casillas—, no
   * un permiso en sí. Por eso queda a medias cuando solo algunas están puestas.
   */
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { base } from '$app/paths';
  import { Badge, Button, Checkbox, StatusToggle } from '$lib/ds';
  import { branding } from '$lib/branding.svelte';
  import { rolesState as rs } from '$lib/roles.svelte';

  const id = $derived(page.params.id);

  /** Los códigos marcados. Se trabaja sobre una copia hasta guardar. */
  let selected = $state<string[]>([]);
  let original = $state<string[]>([]);
  let saved = $state(false);

  const dirty = $derived(
    selected.length !== original.length ||
    selected.some((c) => !original.includes(c)),
  );

  onMount(async () => {
    await rs.load(id);
    sync();
  });

  function sync() {
    const actuales = rs.current?.permissions ?? [];
    selected = [...actuales];
    original = [...actuales];
  }

  function toggle(code: string) {
    selected = selected.includes(code)
      ? selected.filter((c) => c !== code)
      : [...selected, code];
    saved = false;
  }

  function moduleState(codes: string[]): 'todos' | 'algunos' | 'ninguno' {
    const puestos = codes.filter((c) => selected.includes(c)).length;
    if (puestos === 0) return 'ninguno';
    return puestos === codes.length ? 'todos' : 'algunos';
  }

  function toggleModule(codes: string[]) {
    const estado = moduleState(codes);
    selected = estado === 'todos'
      ? selected.filter((c) => !codes.includes(c))
      : [...new Set([...selected, ...codes])];
    saved = false;
  }

  function discard() {
    selected = [...original];
    saved = false;
  }

  async function save() {
    saved = false;
    if (await rs.savePermissions(id, selected)) {
      original = [...selected];
      saved = true;
    }
  }
</script>

<svelte:head>
  <title>{rs.current?.name ?? 'Rol'} · {branding.data.name}</title>
</svelte:head>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <a class="crumb light" href="{base}/settings">CONFIGURACIÓN</a>
    <span class="sep">/</span>
    <a class="crumb light" href="{base}/settings/roles">ROLES</a>
    <span class="sep">/</span>
    <span class="crumb dark">{(rs.current?.name ?? '').toUpperCase()}</span>
  </nav>

  {#if rs.loading}
    <p class="muted">Cargando…</p>
  {:else if !rs.current}
    <p class="muted">No se encontró el rol.</p>
  {:else}
    <header class="head">
      <div class="head-main">
        <h1 class="title">
          {rs.current.name}
          {#if rs.current.is_system}<Badge variant="neutral" size="sm">del sistema</Badge>{/if}
        </h1>
        <p class="sub">
          {rs.current.description || 'Sin descripción.'}
          · <strong>{rs.current.scope_label}</strong>
          · {rs.current.people} persona(s)
        </p>
      </div>
      <div class="head-actions">
        {#if dirty}<Badge variant="warning" size="sm">Sin guardar</Badge>{/if}
        {#if saved && !dirty}<Badge variant="success" size="sm">Guardado</Badge>{/if}
      </div>
    </header>

    {#if rs.current.scope === 'PROJECT'}
      <p class="notice">
        Este rol se cumple <strong>dentro de un proyecto</strong>, no en toda la
        institución. Los permisos de abajo se le aplicarán cuando exista la
        asignación por proyecto; hoy no tienen efecto.
      </p>
    {/if}

    {#if rs.errorMessage}
      <p class="error">{rs.errorMessage}</p>
    {/if}

    <section class="panel">
      {#each rs.catalog as modulo (modulo.module)}
        {@const codes = modulo.permissions.map((p) => p.code)}
        {@const estado = moduleState(codes)}
        <div class="modulo">
          <div class="modulo-head">
            <StatusToggle
              isActive={estado === 'todos'}
              activeLabel={modulo.module}
              inactiveLabel={modulo.module}
              onToggle={() => toggleModule(codes)}
            />
            <span class="modulo-count" class:parcial={estado === 'algunos'}>
              {codes.filter((c) => selected.includes(c)).length} de {codes.length}
            </span>
          </div>

          <div class="permisos">
            {#each modulo.permissions as permiso (permiso.code)}
              <Checkbox
                checked={selected.includes(permiso.code)}
                label={permiso.description}
                onchange={() => toggle(permiso.code)}
              />
            {/each}
          </div>
        </div>
      {/each}
    </section>

    <footer class="actions">
      <Button variant="outline" onclick={discard} disabled={!dirty || rs.saving}>
        Descartar
      </Button>
      <Button variant="primary" loading={rs.saving} disabled={!dirty || rs.saving}
              onclick={save}>
        Guardar
      </Button>
    </footer>
  {/if}
</main>

<style>
  .page { max-width: 920px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; flex-wrap: wrap; }
  .crumb.light { color: var(--ds-neutral-500, #94a3b8); text-decoration: none; }
  .crumb.light:hover { color: var(--ds-brand-500); }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }
  .sep { color: var(--ds-neutral-400, #cbd5e1); }

  .head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .head-main { min-width: 0; }
  .title {
    margin: 0; font-size: 24px; font-weight: 800; color: var(--ds-neutral-800, #1e293b);
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  }
  .sub { margin: 5px 0 0; font-size: 13px; color: var(--ds-neutral-500, #64748b); }
  .head-actions { display: flex; align-items: center; gap: 8px; }

  .panel {
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; overflow: hidden;
  }

  .modulo { border-bottom: 1px solid var(--ds-neutral-100, #f1f5f9); }
  .modulo:last-child { border-bottom: none; }

  .modulo-head {
    display: flex; align-items: center; gap: 14px;
    padding: 16px 22px; background: var(--ds-neutral-100, #f8fafc);
  }
  .modulo-name { font-size: 14px; font-weight: 700; color: var(--ds-neutral-800, #1e293b); flex: 1; }
  .modulo-count {
    font-size: 11px; font-weight: 600; color: var(--ds-neutral-500, #64748b);
    font-variant-numeric: tabular-nums;
  }
  /* A medias se marca en el contador: el interruptor solo sabe de encendido
     y apagado, y un módulo con la mitad puesta no puede verse como vacío. */
  .modulo-count.parcial { color: var(--ds-brand-600); }

  /* El interruptor y las casillas los traen `StatusToggle` y `Checkbox`. */
  .permisos {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 6px 24px; padding: 16px 22px 20px;
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
</style>
