<script lang="ts">
  /* Barra superior.
   *
   * OJO: en el monorepo de InnoTech el navbar **no vive en los
   * microfrontends** — lo pone el shell (`shell-sv/routes/(app)/+layout.svelte`)
   * y los MFE se montan dentro. `academic-sv` no tiene navbar propio.
   *
   * Este existe porque el proyecto corre solo. Es deliberadamente simple: el
   * de InnoTech depende de `@innotech/auth`, de las membresías del usuario y
   * de dos modales (cambio de institución y de rol) que acá no existen.
   *
   * Para integrar: se borra este componente y su uso en `+layout.svelte`.
   */
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import { branding } from '$lib/branding.svelte';
  import { auth } from '$lib/auth.svelte';
  import Icon from '$lib/ds/Icon.svelte';

  let menuOpen = $state(false);

  function go(path: string) {
    menuOpen = false;
    goto(`${base}${path}`);
  }
</script>

<header class="nav">
  <div class="nav-in">
    <div class="nav-brand">
      <!-- La inicial hace de logo mientras no haya uno configurado. -->
      <span class="nav-logo">{branding.data.name.charAt(0)}</span>
      <div class="nav-titles">
        <strong>{branding.data.name}</strong>
        <span>Vinculación con la Sociedad</span>
      </div>
    </div>

    <div class="nav-user-wrap">
      <button class="nav-user" onclick={() => (menuOpen = !menuOpen)}>
        <Icon name="user/user" size="md" />
        <span>{auth.user?.full_name || auth.user?.username || 'Invitado'}</span>
      </button>

      {#if menuOpen}
        <div class="nav-menu">
          <button class="nav-menu-item" onclick={() => go('/settings/branding')}>
            Identidad visual
          </button>
          <div class="nav-menu-sep"></div>
          <button class="nav-menu-item" onclick={() => auth.signOut()}>
            Cerrar sesión
          </button>
        </div>
      {/if}
    </div>
  </div>
</header>

<style>
  .nav {
    background: #fff;
    border-bottom: 1px solid var(--ds-neutral-200, #e2e8f0);
    position: sticky; top: 0; z-index: 50;
  }
  .nav-in {
    max-width: 1180px; margin: 0 auto; padding: 12px 24px;
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
  }
  .nav-brand { display: flex; align-items: center; gap: 12px; }
  .nav-logo {
    width: 38px; height: 38px; border-radius: 10px;
    background: var(--ds-brand-500); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 17px;
  }
  .nav-titles { display: flex; flex-direction: column; line-height: 1.25; }
  .nav-titles strong { font-size: 14px; color: var(--ds-neutral-800, #1e293b); }
  .nav-titles span { font-size: 11px; color: var(--ds-neutral-500, #64748b); }

  .nav-user-wrap { position: relative; }
  .nav-user {
    display: flex; align-items: center; gap: 8px; border: 0; cursor: pointer;
    font-size: 13px; font-family: inherit; color: var(--ds-neutral-600, #475569);
    padding: 6px 12px; border-radius: 999px;
    background: var(--ds-neutral-100, #f1f5f9);
  }
  .nav-user:hover { background: var(--ds-neutral-200, #e2e8f0); }
  .nav-menu {
    position: absolute; right: 0; top: calc(100% + 6px); min-width: 170px;
    background: #fff; border: 1px solid var(--ds-neutral-200, #e2e8f0);
    border-radius: 10px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
    padding: 5px; z-index: 60;
  }
  .nav-menu-item {
    width: 100%; text-align: left; border: 0; background: transparent;
    font-family: inherit; font-size: 13px; color: var(--ds-neutral-700, #334155);
    padding: 8px 10px; border-radius: 7px; cursor: pointer;
  }
  .nav-menu-item:hover { background: var(--ds-neutral-100, #f1f5f9); }
  .nav-menu-sep {
    height: 1px; margin: 4px 6px;
    background: var(--ds-neutral-200, #e2e8f0);
  }
</style>
