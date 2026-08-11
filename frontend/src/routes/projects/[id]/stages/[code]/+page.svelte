<script lang="ts">
  /**
   * Pantalla de una etapa del proyecto.
   *
   * Réplica de `view-pe-idea`, `view-pe-incubacion` y las demás del mockup:
   * una tarjeta por actividad, cada una con sus acciones y una rejilla de
   * Responsable · Fecha · Estado.
   *
   * "Formulación de la Idea" no se puede confirmar a mano: se marca sola
   * cuando el proyecto ya eligió sus actividades en Incubación y
   * Post-incubación. El botón lo refleja.
   */
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import { Badge, Button, Icon } from '$lib/ds';
  import { projectState as ps, type Activity } from '$lib/project.svelte';

  const id = $derived(page.params.id);
  const code = $derived(page.params.code);

  onMount(() => ps.load(id));

  const stage = $derived(ps.stage(code));
  const applicable = $derived(stage ? stage.activities.filter((a) => a.applies) : []);
  const available = $derived(
    stage ? stage.activities.filter((a) => a.is_optional && !a.applies) : [],
  );
</script>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <a class="crumb light" href={base || "/"}>PROYECTOS DE EMPRENDIMIENTO</a>
    <span class="sep">/</span>
    <a class="crumb light" href="{base}/projects/{id}">TABLERO</a>
    <span class="sep">/</span>
    <span class="crumb dark">{stage?.name?.toUpperCase() ?? ''}</span>
  </nav>

  {#if ps.loading}
    <p class="muted">Cargando…</p>
  {:else if ps.errorMessage}
    <p class="error">{ps.errorMessage}</p>
  {:else if !stage}
    <p class="muted">No se encontró la etapa.</p>
  {:else}
    <header class="head">
      <h1 class="title">{stage.name}</h1>
      <div class="head-actions">
        <Badge variant="neutral" size="lg">{stage.progress}% completado</Badge>
        <Button variant="outline" size="md" onclick={() => goto(`${base}/projects/${id}`)}>
          Regresar
        </Button>
      </div>
    </header>

    {#if applicable.length === 0}
      <div class="empty">
        <p class="empty-title">No se han definido actividades para esta etapa</p>
        <p class="empty-sub">
          Las actividades de esta etapa se eligen en
          <strong>Formulación de la Idea</strong>.
        </p>
        <Button
          variant="outline" size="md"
          onclick={() => goto(`${base}/projects/${id}/stages/IDEA`)}
        >
          Ir a Formulación de la Idea
        </Button>
      </div>
    {:else}
      <div class="cards">
        {#each applicable as a (a.id)}
          <article class="act" class:is-done={a.is_confirmed}>
            <header class="act-head">
              <h2>{a.name}</h2>
              <div class="act-actions">
                <Button variant="outline" size="sm">Editar</Button>
                <Button variant="outline" size="sm">Ver</Button>
                {#if a.is_derived}
                  <!-- Derivada: no se marca a mano. -->
                  <Button
                    variant={a.is_confirmed ? 'success' : 'outline'}
                    size="sm" disabled
                    title="Se marca automáticamente al elegir las actividades de Incubación y Post-incubación"
                  >
                    {a.is_confirmed ? 'Confirmado' : 'Automático'}
                  </Button>
                {:else}
                  <Button
                    variant={a.is_confirmed ? 'success' : 'outline'}
                    size="sm"
                    onclick={() => ps.toggleConfirmed(a)}
                  >
                    {#snippet prefix()}
                      <Icon name={a.is_confirmed ? 'system/edit' : 'files/document'} size="sm" />
                    {/snippet}
                    {a.is_confirmed ? 'Confirmado' : 'Confirmar'}
                  </Button>
                {/if}
                {#if a.is_optional}
                  <button class="link-btn" onclick={() => ps.toggleApplies(a)}>
                    Quitar
                  </button>
                {/if}
              </div>
            </header>

            <!-- Rejilla del mockup. Todavía sin datos: quién es responsable y
                 en qué fecha son campos que el proceso no tiene definidos. -->
            <div class="grid">
              <div class="cell"><span class="k">Responsable</span><span class="v">—</span></div>
              <div class="cell"><span class="k">Fecha</span><span class="v">—</span></div>
              <div class="cell">
                <span class="k">Estado</span>
                <span class="v">{a.is_confirmed ? 'Confirmado' : 'Pendiente'}</span>
              </div>
            </div>
          </article>
        {/each}
      </div>
    {/if}

    {#if available.length}
      <section class="available">
        <p class="available-title">Actividades que se pueden sumar a esta etapa</p>
        <div class="chips">
          {#each available as a (a.id)}
            <button class="chip" onclick={() => ps.toggleApplies(a)}>
              <Icon name="system/plus" size="sm" />
              {a.name}
            </button>
          {/each}
        </div>
      </section>
    {/if}
  {/if}
</main>

<style>
  .page { max-width: 1180px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; flex-wrap: wrap; }
  .crumb.light { color: var(--ds-neutral-500, #94a3b8); text-decoration: none; }
  .crumb.light:hover { color: var(--ds-brand-500); }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }
  .sep { color: var(--ds-neutral-400, #cbd5e1); }

  .head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .title { margin: 0; font-size: 22px; font-weight: 800; color: var(--ds-neutral-800, #1e293b); }
  .head-actions { display: flex; align-items: center; gap: 10px; }

  .cards { display: flex; flex-direction: column; gap: 16px; }

  .act {
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; overflow: hidden;
  }
  .act.is-done { border-color: var(--ds-success-300, #C2F4D6); }

  .act-head {
    display: flex; align-items: center; justify-content: space-between;
    gap: 14px; flex-wrap: wrap; padding: 16px 20px;
  }
  .act-head h2 {
    margin: 0; font-size: 17px; font-weight: 600;
    color: var(--ds-neutral-600, #64748B);
  }
  .act-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

  .grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    border-top: 1px solid var(--ds-neutral-100, #eef2f7);
  }
  .cell {
    display: flex; flex-direction: column; gap: 4px; padding: 14px 20px;
    border-right: 1px solid var(--ds-neutral-100, #eef2f7);
  }
  .cell:last-child { border-right: none; }
  .k { font-size: 13px; font-weight: 600; color: var(--ds-neutral-500, #647496); }
  .v { font-size: 12px; font-weight: 500; color: var(--ds-neutral-700, #334155); text-transform: uppercase; }

  .link-btn {
    border: 0; background: transparent; cursor: pointer; font-family: inherit;
    font-size: 12px; color: var(--ds-neutral-500, #64748b); padding: 4px 8px; border-radius: 5px;
  }
  .link-btn:hover { background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-600); }

  .empty {
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; padding: 40px 24px; text-align: center;
    display: flex; flex-direction: column; align-items: center; gap: 6px;
  }
  .empty-title { margin: 0; font-size: 15px; font-weight: 600; color: var(--ds-neutral-600, #475569); }
  .empty-sub { margin: 0 0 10px; font-size: 13px; color: var(--ds-neutral-500, #647496); }

  .available {
    background: #fff; border: 1px dashed var(--ds-neutral-300, #e2e8f0);
    border-radius: 12px; padding: 16px 20px;
  }
  .available-title { margin: 0 0 10px; font-size: 12px; font-weight: 600; color: var(--ds-neutral-500, #64748b); }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip {
    display: inline-flex; align-items: center; gap: 5px;
    border: 1px dashed var(--ds-neutral-300, #cbd5e1); background: #fff;
    color: var(--ds-neutral-600, #475569); font-family: inherit; font-size: 13px;
    padding: 6px 12px; border-radius: 999px; cursor: pointer;
  }
  .chip:hover { border-color: var(--ds-brand-500); color: var(--ds-brand-600); background: var(--ds-brand-100); }

  .muted { color: var(--ds-neutral-500, #64748b); font-size: 13px; }
  .error {
    margin: 0; padding: 10px 14px; border-radius: 8px; font-size: 13px;
    background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700);
    border: 1px solid var(--ds-error-300);
  }

  @media (max-width: 620px) { .grid { grid-template-columns: 1fr; } .cell { border-right: none; border-bottom: 1px solid var(--ds-neutral-100, #eef2f7); } }
</style>
