<script lang="ts">
  /**
   * Roles del proceso.
   *
   * Se listan separados en dos bloques —cargos y papeles de proyecto— porque
   * son cosas distintas: un cargo se es siempre, un papel se es dentro de un
   * proyecto concreto. Los permisos de módulo solo significan algo en los
   * primeros; mezclarlos en una lista sola confunde a quien reparte.
   */
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import {
    Badge, Button, ConfirmModal, Icon, Modal, RowActions, Select, Table,
    TableBody, TableCell, TableHead, TableHeadCell, TableRow, TextArea, TextField,
  } from '$lib/ds';
  import { branding } from '$lib/branding.svelte';
  import { rolesState as rs, type Role } from '$lib/roles.svelte';

  onMount(() => rs.loadAll());

  let createOpen = $state(false);
  let newName = $state('');
  let newDescription = $state('');
  let cloneFrom = $state('');

  let removing = $state<Role | null>(null);

  const cloneOptions = $derived([
    { value: '', label: 'Sin permisos' },
    ...rs.roles.map((r) => ({ value: r.id, label: r.name })),
  ]);

  function openCreate() {
    newName = '';
    newDescription = '';
    cloneFrom = '';
    createOpen = true;
  }

  async function create() {
    if (!newName.trim()) return;
    const created = await rs.create(newName, newDescription, cloneFrom);
    if (!created) return;
    createOpen = false;
    // Recién creado no tiene permisos que mirar en la lista: lo que sigue es
    // repartírselos.
    goto(`${base}/settings/roles/${created.id}`);
  }

  async function confirmRemove() {
    if (!removing) return;
    if (await rs.remove(removing.id)) removing = null;
  }

  function actionsFor(role: Role) {
    return [
      {
        icon: 'interface/settings',
        title: 'Ver permisos',
        onclick: () => goto(`${base}/settings/roles/${role.id}`),
      },
      {
        icon: 'system/trash',
        title: role.is_system ? 'No se puede eliminar' : 'Eliminar',
        disabled: role.is_system,
        onclick: () => (removing = role),
      },
    ];
  }
</script>

<svelte:head><title>Roles · {branding.data.name}</title></svelte:head>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <a class="crumb light" href="{base}/settings">CONFIGURACIÓN</a>
    <span class="sep">/</span>
    <span class="crumb dark">ROLES</span>
  </nav>

  <header class="head">
    <div>
      <h1 class="title">Roles</h1>
      <p class="sub">
        Un rol es un conjunto de permisos. Los permisos en sí los trae el
        sistema; acá se decide qué puede hacer cada quien.
      </p>
    </div>
    <Button variant="primary" size="md" onclick={openCreate}>
      {#snippet prefix()}<Icon name="system/plus" size="sm" />{/snippet}
      Nuevo rol
    </Button>
  </header>

  {#if rs.errorMessage}
    <p class="error">{rs.errorMessage}</p>
  {/if}

  {#if rs.loading}
    <p class="muted">Cargando…</p>
  {:else}
    {#each [{ titulo: 'Cargos en la institución', nota: 'Se es siempre, en todo proyecto.', lista: rs.institutional }, { titulo: 'Papeles dentro de un proyecto', nota: 'Se es de un proyecto concreto. Los permisos de módulo todavía no aplican acá: falta la asignación por proyecto.', lista: rs.perProject }] as grupo (grupo.titulo)}
      <section class="grupo">
        <div class="grupo-head">
          <h2>{grupo.titulo}</h2>
          <p>{grupo.nota}</p>
        </div>

        <div class="table-wrap ds-datos-mayuscula">
          <Table>
            <TableHead>
              <TableRow>
                <TableHeadCell>Rol</TableHeadCell>
                <TableHeadCell>Descripción</TableHeadCell>
                <TableHeadCell width="120px">Permisos</TableHeadCell>
                <TableHeadCell width="120px">Personas</TableHeadCell>
                <TableHeadCell width="110px" align="right">Gestión</TableHeadCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {#if grupo.lista.length === 0}
                <TableRow>
                  <TableCell class="empty" colspan="5">Ninguno todavía.</TableCell>
                </TableRow>
              {:else}
                {#each grupo.lista as role (role.id)}
                  <TableRow>
                    <TableCell class="col-name">
                      {role.name}
                      {#if role.is_system}
                        <Badge variant="neutral" size="sm">del sistema</Badge>
                      {/if}
                    </TableCell>
                    <TableCell class="col-desc">{role.description || '—'}</TableCell>
                    <TableCell>{role.permission_count}</TableCell>
                    <TableCell>{role.people}</TableCell>
                    <TableCell align="right">
                      <RowActions actions={actionsFor(role)} expanded />
                    </TableCell>
                  </TableRow>
                {/each}
              {/if}
            </TableBody>
          </Table>
        </div>
      </section>
    {/each}
  {/if}
</main>

<Modal bind:open={createOpen} title="Nuevo rol" size="md">
  {#snippet children()}
    <div class="form">
      <TextField label="Nombre del rol" bind:value={newName} placeholder="Ej. Revisor Externo" />
      <TextArea label="Descripción" bind:value={newDescription} rows={2}
                placeholder="Para qué sirve este rol…" />
      <div>
        <Select label="Copiar permisos de" options={cloneOptions} bind:value={cloneFrom} />
        <span class="hint">
          Casi siempre un rol nuevo se parece a uno que ya existe. Después se ajusta.
        </span>
      </div>
    </div>
  {/snippet}
  {#snippet footer()}
    <Button variant="outline" onclick={() => (createOpen = false)}>Cancelar</Button>
    <Button variant="primary" loading={rs.saving} disabled={!newName.trim() || rs.saving}
            onclick={create}>
      Crear
    </Button>
  {/snippet}
</Modal>

<ConfirmModal
  open={!!removing}
  variant="delete"
  title="Eliminar rol"
  message={removing ? `"${removing.name}" se elimina definitivamente.` : ''}
  primaryLabel="Eliminar"
  loading={rs.saving}
  onConfirm={confirmRemove}
  onCancel={() => (removing = null)}
/>

<style>
  .page { max-width: 1080px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 24px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; }
  .crumb.light { color: var(--ds-neutral-500, #94a3b8); text-decoration: none; }
  .crumb.light:hover { color: var(--ds-brand-500); }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }
  .sep { color: var(--ds-neutral-400, #cbd5e1); }

  .head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .title { margin: 0; font-size: 24px; font-weight: 800; color: var(--ds-neutral-800, #1e293b); }
  .sub { margin: 4px 0 0; font-size: 13px; color: var(--ds-neutral-500, #64748b); max-width: 62ch; }

  .grupo { display: flex; flex-direction: column; gap: 10px; }
  .grupo-head h2 { margin: 0; font-size: 15px; font-weight: 700; color: var(--ds-neutral-800, #1e293b); }
  .grupo-head p { margin: 3px 0 0; font-size: 12.5px; color: var(--ds-neutral-500, #64748b); max-width: 70ch; }

  .table-wrap {
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; overflow: hidden;
  }
  .table-wrap :global(.col-name) {
    font-weight: 600; color: var(--ds-neutral-800, #1e293b);
    display: flex; align-items: center; gap: 8px;
  }
  .table-wrap :global(.col-desc) { color: var(--ds-neutral-500, #64748b); }
  .table-wrap :global(.empty) { text-align: center; padding: 28px 16px; color: var(--ds-neutral-400, #94a3b8); }

  .form { display: flex; flex-direction: column; gap: 16px; }
  .hint { font-size: 11px; color: var(--ds-neutral-400, #94a3b8); }

  .muted { color: var(--ds-neutral-500, #64748b); font-size: 13px; }
  .error {
    margin: 0; padding: 10px 14px; border-radius: 8px; font-size: 13px;
    background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700);
    border: 1px solid var(--ds-error-300);
  }
</style>
