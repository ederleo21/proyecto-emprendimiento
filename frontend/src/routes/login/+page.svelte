<script lang="ts">
  /**
   * Pantalla de acceso.
   *
   * El token lo emite este servicio, no el IAM de InnoTech: el proyecto tiene
   * que poder usarse sin depender de aquel stack.
   *
   * Embebida en el shell esta pantalla no se ve: allá la sesión llega hecha,
   * por el fragmento de la URL. Ver `lib/session.ts`.
   */
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  import { Button, TextField } from '$lib/ds';
  import { auth } from '$lib/auth.svelte';
  import { branding } from '$lib/branding.svelte';

  let username = $state('');
  let password = $state('');

  const valid = $derived(!!username.trim() && !!password);

  async function submit(e?: Event) {
    e?.preventDefault();
    if (!valid || auth.loading) return;
    const ok = await auth.signIn(username.trim(), password);
    if (ok) goto(base || '/');
  }
</script>

<svelte:head><title>Acceso · {branding.data.name}</title></svelte:head>

<main class="wrap">
  <form class="card" onsubmit={submit}>
    <div class="brand">
      <span class="logo">{branding.data.name.charAt(0)}</span>
      <div>
        <strong>{branding.data.name}</strong>
        <span class="sub">Vinculación con la Sociedad</span>
      </div>
    </div>

    <h1>Iniciar sesión</h1>

    <TextField label="Usuario" bind:value={username} placeholder="admin" />
    <TextField label="Contraseña" type="password" bind:value={password} placeholder="••••••••" />

    {#if auth.errorMessage}
      <p class="error">{auth.errorMessage}</p>
    {/if}

    <Button
      variant="primary" size="lg" fullWidth type="submit"
      loading={auth.loading} disabled={!valid || auth.loading}
      onclick={submit}
    >
      Entrar
    </Button>
  </form>
</main>

<style>
  .wrap {
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    padding: 24px; background: var(--ds-neutral-100, #f6f8fb);
  }
  .card {
    width: 100%; max-width: 380px; background: #fff;
    border: 1px solid var(--ds-neutral-200, #e2e8f0); border-radius: 14px;
    padding: 28px; display: flex; flex-direction: column; gap: 16px;
    box-shadow: 0 8px 28px rgba(15, 23, 42, 0.06);
  }
  .brand { display: flex; align-items: center; gap: 12px; }
  .logo {
    width: 42px; height: 42px; border-radius: 11px;
    background: var(--ds-brand-500); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 19px;
  }
  .brand strong { display: block; font-size: 14px; color: var(--ds-neutral-800, #1e293b); }
  .brand .sub { font-size: 11px; color: var(--ds-neutral-500, #64748b); }
  h1 { margin: 4px 0 0; font-size: 19px; color: var(--ds-neutral-800, #1e293b); }
  .error {
    margin: 0; padding: 9px 12px; border-radius: 8px; font-size: 13px;
    background: var(--ds-error-100, #FFE9E9); color: var(--ds-error-700);
    border: 1px solid var(--ds-error-300);
  }
</style>
