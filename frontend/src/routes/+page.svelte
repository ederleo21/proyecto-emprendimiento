<script lang="ts">
  /**
   * Proyectos de Emprendimiento — pantalla principal.
   *
   * Réplica de la vista del mockup `Proyecto de Emprendimiento.html`:
   * métricas por etapa, barra de filtros, tabla y el modal de creación.
   *
   * Las reglas del proceso todavía no están definidas, así que la pantalla no
   * asume ninguna: no hay avance de etapa, ni aprobaciones, ni permisos. Solo
   * listar, filtrar y dar de alta.
   */
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import {
    Badge, Button, Icon, Modal, Pagination, ProgressBar, Select, StatCards,
    Table, TableBody, TableCell, TableHead, TableHeadCell, TableRow,
    TextField, ViewToggle,
  } from '$lib/ds';
  import { projectsState as ps } from '$lib/projects.svelte';

  onMount(() => ps.loadAll());

  let modalOpen = $state(false);
  let newTitle = $state('');

  function openCreate() {
    newTitle = '';
    modalOpen = true;
  }

  async function save() {
    if (!newTitle.trim()) return;
    const created = await ps.createProject(newTitle);
    if (!created) return;
    modalOpen = false;
    // Recién creado no tiene nada marcado: llevarlo al tablero es lo que
    // sigue, en vez de dejarlo buscando su fila en la tabla.
    goto(`${base}/projects/${created.id}`);
  }

  // Al filtrar se relee solo el listado; las métricas no cambian. Se vuelve a
  // la primera página porque con el filtro nuevo la actual puede no existir.
  function onStageChange(value: string) {
    ps.stageFilter = value;
    ps.applyFilters();
  }
  function onSearchInput(value: string) {
    ps.search = value;
    ps.applyFilters();
  }
</script>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <span class="crumb light">INICIO</span>
    <span class="sep">/</span>
    <span class="crumb dark">PROYECTOS DE EMPRENDIMIENTO</span>
  </nav>

  <h1 class="title">Proyecto de Emprendimiento</h1>

  <!-- Métricas por etapa. Se muestran todas, incluidas las que están en cero:
       si aparecieran solo las que tienen datos, la fila cambiaría de ancho. -->
  <section aria-label="Proyectos por etapa">
    <StatCards items={ps.statItems} />
  </section>

  <!-- Barra de herramientas -->
  <section class="toolbar">
    <div class="toolbar-filters">
      <ViewToggle bind:value={ps.view} />

      <div class="filter">
        <Select
          label="Etapa"
          options={ps.stageOptions}
          value={ps.stageFilter}
          size="sm"
          onchange={onStageChange}
        />
      </div>

      <div class="filter filter-grow">
        <TextField
          label="Búsqueda"
          placeholder="Nombre del proyecto"
          value={ps.search}
          size="sm"
          oninput={onSearchInput}
        />
      </div>
    </div>

    <Button variant="primary" size="md" onclick={openCreate}>
      {#snippet prefix()}<Icon name="system/plus" size="sm" />{/snippet}
      Disponer Creación
    </Button>
  </section>

  {#if ps.errorMessage}
    <p class="error">{ps.errorMessage}</p>
  {/if}

  <!-- Listado -->
  <section class="table-wrap">
    {#if ps.view === 'table'}
      <Table>
        <TableHead>
          <TableRow>
            <TableHeadCell>Título</TableHeadCell>
            <TableHeadCell width="200px">Etapa Actual</TableHeadCell>
            <TableHeadCell width="200px">Avance</TableHeadCell>
            <TableHeadCell width="100px" align="right">Gestión</TableHeadCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {#if ps.loading}
            <TableRow>
              <TableCell class="empty" colspan="4">
                <div class="empty-title">Cargando…</div>
              </TableCell>
            </TableRow>
          {:else if ps.projects.length === 0}
            <TableRow>
              <TableCell class="empty" colspan="4">
                <div class="empty-title">No se encontraron proyectos de emprendimiento</div>
                <div class="empty-sub">Intenta ajustar los filtros de búsqueda</div>
              </TableCell>
            </TableRow>
          {:else}
            {#each ps.projects as p (p.id)}
              <TableRow>
                <TableCell class="col-title">{p.title}</TableCell>
                <TableCell>
                  {#if p.stage_name}
                    <Badge variant="primary" size="sm">{p.stage_name}</Badge>
                  {:else}
                    <span class="muted">Sin etapa</span>
                  {/if}
                </TableCell>
                <TableCell>
                  <ProgressBar value={p.progress} showValue />
                </TableCell>
                <TableCell align="right">
                  <button
                    class="row-btn"
                    onclick={() => goto(`${base}/projects/${p.id}`)}
                    aria-label="Abrir tablero del proyecto"
                    title="Abrir tablero"
                  >
                    <Icon name="arrows/chevron-right" size="sm" />
                  </button>
                </TableCell>
              </TableRow>
            {/each}
          {/if}
        </TableBody>
      </Table>
    {:else}
      <div class="cards">
        {#if ps.projects.length === 0}
          <div class="empty">
            <div class="empty-title">No se encontraron proyectos de emprendimiento</div>
            <div class="empty-sub">Intenta ajustar los filtros de búsqueda</div>
          </div>
        {:else}
          {#each ps.projects as p (p.id)}
            <!-- Botón y no `article`: la tarjeta entera abre el tablero, así
                 que tiene que ser operable con teclado sin trucos de rol. -->
            <button class="card" onclick={() => goto(`${base}/projects/${p.id}`)}>
              <span class="card-title">{p.title}</span>
              {#if p.stage_name}<Badge variant="primary" size="sm">{p.stage_name}</Badge>{/if}
              <ProgressBar value={p.progress} showValue />
            </button>
          {/each}
        {/if}
      </div>
    {/if}

    <footer class="table-foot">
      <Pagination
        currentPage={ps.page}
        totalPages={ps.totalPages}
        totalItems={ps.total}
        pageSize={ps.pageSize}
        onPageChange={(p) => ps.goToPage(p)}
      />
    </footer>
  </section>
</main>

<!-- Modal de alta. El campo es un textarea porque el mockup pide el contexto
     o la motivación institucional, no un título corto. -->
<Modal bind:open={modalOpen} title="Proyecto de Emprendimiento" size="md">
  {#snippet children()}
    <TextField
      label="Título"
      multiline
      rows={3}
      bind:value={newTitle}
      placeholder="Contexto o motivación institucional del proyecto…"
    />
  {/snippet}
  {#snippet footer()}
    <Button variant="outline" onclick={() => (modalOpen = false)}>Cancelar</Button>
    <Button
      variant="primary"
      loading={ps.saving}
      disabled={!newTitle.trim() || ps.saving}
      onclick={save}
    >
      Guardar
    </Button>
  {/snippet}
</Modal>

<style>
  .page { max-width: 1180px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; }
  .crumb.light { color: var(--ds-neutral-500, #94a3b8); }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }
  .sep { color: var(--ds-neutral-400, #cbd5e1); }

  .title { margin: 0; font-size: 24px; font-weight: 800; color: var(--ds-neutral-800, #1e293b); }

  /* Las métricas, la paginación y las barras de avance ya no tienen estilos
     acá: los traen `StatCards`, `Pagination` y `ProgressBar`. */

  /* Barra de herramientas */
  .toolbar {
    display: flex; align-items: flex-end; justify-content: space-between;
    gap: 16px; flex-wrap: wrap;
  }
  .toolbar-filters { display: flex; align-items: flex-end; gap: 12px; flex: 1; flex-wrap: wrap; }
  .filter { min-width: 170px; }
  .filter-grow { flex: 1; min-width: 220px; }

  .error {
    margin: 0; padding: 10px 14px; border-radius: 8px; font-size: 13px;
    background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700);
    border: 1px solid var(--ds-error-300);
  }

  /* La tabla la pintan `Table`, `TableHead` y compañía. Acá solo queda lo
     propio de esta pantalla, que ellos no pueden saber. */
  .table-wrap {
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; overflow: hidden;
  }
  /* `:global` porque estos estilos aplican dentro de un componente ajeno. */
  .table-wrap :global(.col-title) {
    font-weight: 600; color: var(--ds-neutral-800, #1e293b); max-width: 420px;
  }
  .table-wrap :global(.empty) { text-align: center; padding: 44px 16px; }

  .muted { color: var(--ds-neutral-400, #94a3b8); font-size: 12px; }
  .empty-title { font-size: 14px; font-weight: 600; color: var(--ds-neutral-600, #475569); }
  .empty-sub { font-size: 13px; color: var(--ds-neutral-400, #94a3b8); margin-top: 4px; }

  .row-btn {
    border: 0; background: transparent; cursor: pointer; padding: 5px;
    border-radius: 6px; color: var(--ds-neutral-500, #64748b);
  }
  .row-btn:hover { background: var(--ds-neutral-100, #f1f5f9); }

  /* Vista de tarjetas */
  .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding: 16px; }
  .card {
    border: 1px solid var(--ds-neutral-200, #eef2f6); border-radius: 10px;
    padding: 14px; display: flex; flex-direction: column; align-items: flex-start;
    gap: 10px; cursor: pointer; text-align: left; background: #fff;
    font-family: inherit; width: 100%;
  }
  .card:hover { border-color: var(--ds-brand-500); }
  .card:focus-visible { outline: 2px solid var(--ds-brand-500); outline-offset: 2px; }
  .card-title { font-size: 13px; font-weight: 600; color: var(--ds-neutral-800, #1e293b); }

  /* `Pagination` trae su propio alto y espaciado: acá solo la línea que la
     separa de la tabla. */
  .table-foot { border-top: 1px solid var(--ds-neutral-200, #eef2f6); }

  @media (max-width: 1000px) {
    .cards { grid-template-columns: 1fr; }
  }
</style>
