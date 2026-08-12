<script lang="ts">
  /**
   * Tablero de un proyecto de emprendimiento.
   *
   * Réplica de `view-pe-dashboard` del mockup: una tarjeta por etapa con su
   * barra de avance. La tarjeta **navega** a la pantalla de esa etapa; no
   * despliega nada acá.
   *
   * El color de la barra sale del porcentaje, no de la etapa: rojo cuando no
   * ha empezado, naranja en curso, verde terminada.
   */
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import { Badge, Button, Icon, ProgressBar, Select } from '$lib/ds';
  import { projectState as ps, type ProjectStage } from '$lib/project.svelte';

  const id = $derived(page.params.id);

  onMount(() => ps.load(id));

  // El color sale del porcentaje, no de la etapa: rojo si no ha empezado,
  // naranja en curso, verde terminada. Son las variantes de `ProgressBar`.
  function barVariant(pct: number) {
    if (pct === 0) return 'danger' as const;
    if (pct === 100) return 'success' as const;
    return 'warning' as const;
  }

  function applicable(s: ProjectStage) {
    return s.activities.filter((a) => a.applies);
  }
</script>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <a class="crumb light" href={base || "/"}>PROYECTOS DE EMPRENDIMIENTO</a>
    <span class="sep">/</span>
    <span class="crumb dark">TABLERO</span>
  </nav>

  {#if ps.loading}
    <p class="muted">Cargando…</p>
  {:else if ps.errorMessage}
    <p class="error">{ps.errorMessage}</p>
  {:else if ps.project}
    <header class="head">
      <div class="head-main">
        {#if ps.project.code}<span class="code">{ps.project.code}</span>{/if}
        <h1 class="title">{ps.project.title}</h1>
      </div>
      <div class="head-actions">
        <!-- El cambio de etapa es manual: qué la hace avanzar sola todavía no
             está definido, y aun cuando lo esté hará falta poder corregir. -->
        <div class="stage-picker">
          <Select
            label="Etapa actual"
            size="sm"
            options={ps.stageChoices}
            value={ps.project.stage ?? ''}
            onchange={(v) => ps.setStage(v)}
          />
        </div>
        <Badge variant="neutral" size="lg">{ps.project.progress}% completado</Badge>
        <Button variant="outline" size="md" onclick={() => goto(base || '/')}>Regresar</Button>
      </div>
    </header>

    <section class="board">
      {#each ps.stages as s (s.id)}
        <button class="card" onclick={() => goto(`${base}/projects/${id}/stages/${s.code}`)}>
          <span class="card-head">
            <span>{s.name}</span>
            <Icon name="arrows/chevron-right" size="sm" />
          </span>

          <span class="card-body">
            <span class="track">
              <ProgressBar value={s.progress} variant={barVariant(s.progress)} />
            </span>
            <span class="card-meta">
              <span>
                {applicable(s).length} actividad{applicable(s).length === 1 ? '' : 'es'}
              </span>
              <span class="pct">{s.progress}%</span>
            </span>
          </span>
        </button>
      {/each}
    </section>
  {/if}
</main>

<style>
  .page { max-width: 1180px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; }
  .crumb.light { color: var(--ds-neutral-500, #94a3b8); text-decoration: none; }
  .crumb.light:hover { color: var(--ds-brand-500); }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }
  .sep { color: var(--ds-neutral-400, #cbd5e1); }

  .head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .head-main { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
  .title { margin: 0; font-size: 22px; font-weight: 800; color: var(--ds-neutral-800, #1e293b); max-width: 60ch; }
  .code {
    font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600;
    color: var(--ds-neutral-500, #64748b);
  }
  .head-actions { display: flex; align-items: flex-end; gap: 12px; flex-wrap: wrap; }
  .stage-picker { min-width: 190px; }

  .board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }

  /* Botón y no `article`: la tarjeta entera navega, así que tiene que ser
     operable con teclado sin trucos de rol. */
  .card {
    display: block; width: 100%; padding: 0; text-align: left;
    font-family: inherit; cursor: pointer;
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; overflow: hidden;
    transition: border-color 0.18s, transform 0.18s;
  }
  .card:hover { border-color: var(--ds-brand-500); transform: translateY(-2px); }
  .card:focus-visible { outline: 2px solid var(--ds-brand-500); outline-offset: 2px; }

  .card-head {
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
    background: var(--ds-brand-500); color: #fff;
    font-weight: 700; font-size: 15px; padding: 13px 16px;
  }
  .card-body { display: block; padding: 24px 20px 16px; }

  /* Solo el hueco: la barra la pinta `ProgressBar`. */
  .track { display: block; margin: 6px 10px 24px; }

  .card-meta {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13px; color: var(--ds-neutral-500, #64748b); font-weight: 500;
  }
  .pct { font-weight: 800; color: var(--ds-neutral-800, #1e293b); font-size: 14px; }

  .muted { color: var(--ds-neutral-500, #64748b); font-size: 13px; }
  .error {
    margin: 0; padding: 10px 14px; border-radius: 8px; font-size: 13px;
    background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700);
    border: 1px solid var(--ds-error-300);
  }

  @media (max-width: 1000px) { .board { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 620px) { .board { grid-template-columns: 1fr; } }
</style>
