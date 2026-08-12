<script lang="ts">
  /**
   * Configuración — índice.
   *
   * En el monorepo de InnoTech cada sección es una carpeta bajo `settings/`
   * (`branding`, `catalog`, `security`…) y se navega desde el menú del shell.
   * Acá el shell no existe, así que esta pantalla hace de índice.
   *
   * Las secciones se declaran en una lista y no como tarjetas escritas a mano:
   * sumar una es una entrada más, no maquetar de nuevo.
   */
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import { Icon } from '$lib/ds';
  import { branding } from '$lib/branding.svelte';

  interface Section {
    path: string;
    icon: string;
    title: string;
    description: string;
    /** Todavía no construida: se muestra apagada en vez de esconderse, para
     *  que se vea qué va a haber. */
    pending?: boolean;
  }

  const SECTIONS: Section[] = [
    {
      path: '/settings/branding',
      icon: 'interface/settings',
      title: 'Identidad visual',
      description: 'Los colores de la institución.',
    },
    {
      path: '/settings/emprendimiento',
      icon: 'files/rocket',
      title: 'Proyecto de Emprendimiento',
      description: 'Cómo se numeran los proyectos y las reglas del módulo.',
    },
    {
      path: '/settings/roles',
      icon: 'user/user',
      title: 'Roles y permisos',
      description: 'Qué puede hacer cada quien.',
    },
    {
      path: '/settings/catalogo',
      icon: 'files/document',
      title: 'Etapas y actividades',
      description: 'El catálogo del proceso.',
      pending: true,
    },
  ];
</script>

<svelte:head><title>Configuración · {branding.data.name}</title></svelte:head>

<main class="page">
  <nav class="breadcrumbs" aria-label="Ruta">
    <span class="crumb dark">CONFIGURACIÓN</span>
  </nav>

  <header>
    <h1 class="title">Configuración</h1>
    <p class="sub">Lo que decide cómo se comporta el módulo en {branding.data.name}.</p>
  </header>

  <section class="grid">
    {#each SECTIONS as s (s.path)}
      <button
        class="card"
        class:pending={s.pending}
        disabled={s.pending}
        onclick={() => goto(`${base}${s.path}`)}
      >
        <span class="card-icon"><Icon name={s.icon} size="md" /></span>
        <span class="card-text">
          <span class="card-title">
            {s.title}
            {#if s.pending}<span class="tag">Pronto</span>{/if}
          </span>
          <span class="card-desc">{s.description}</span>
        </span>
        {#if !s.pending}
          <span class="card-arrow"><Icon name="arrows/chevron-right" size="sm" /></span>
        {/if}
      </button>
    {/each}
  </section>
</main>

<style>
  .page { max-width: 860px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

  .breadcrumbs { display: flex; align-items: center; gap: 8px; font-size: 11px; letter-spacing: 0.05em; }
  .crumb.dark { color: var(--ds-neutral-700, #334155); font-weight: 700; }

  .title { margin: 0; font-size: 24px; font-weight: 800; color: var(--ds-neutral-800, #1e293b); }
  .sub { margin: 4px 0 0; font-size: 13px; color: var(--ds-neutral-500, #64748b); }

  .grid { display: flex; flex-direction: column; gap: 12px; }

  .card {
    display: flex; align-items: center; gap: 16px; width: 100%;
    background: #fff; border: 1px solid var(--ds-neutral-200, #eef2f6);
    border-radius: 12px; padding: 18px 20px; cursor: pointer;
    font-family: inherit; text-align: left;
    transition: border-color 0.15s, transform 0.15s;
  }
  .card:hover:not(.pending) { border-color: var(--ds-brand-500); transform: translateY(-1px); }
  .card:focus-visible { outline: 2px solid var(--ds-brand-500); outline-offset: 2px; }
  .card.pending { cursor: default; opacity: 0.55; }

  .card-icon {
    width: 42px; height: 42px; border-radius: 10px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    background: var(--ds-brand-100); color: var(--ds-brand-500);
  }
  .card-text { display: flex; flex-direction: column; gap: 3px; flex: 1; min-width: 0; }
  .card-title {
    font-size: 14px; font-weight: 700; color: var(--ds-neutral-800, #1e293b);
    display: flex; align-items: center; gap: 8px;
  }
  .card-desc { font-size: 12.5px; color: var(--ds-neutral-500, #64748b); }
  .card-arrow { color: var(--ds-neutral-400, #94a3b8); flex-shrink: 0; }

  .tag {
    font-size: 10px; font-weight: 700; letter-spacing: 0.04em;
    text-transform: uppercase; padding: 2px 7px; border-radius: 999px;
    background: var(--ds-neutral-100, #f1f5f9); color: var(--ds-neutral-500, #64748b);
  }
</style>
