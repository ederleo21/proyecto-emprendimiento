<script lang="ts">
  // Los tokens se cargan acá, una sola vez para toda la aplicación. El
  // branding se pide al arrancar y sobreescribe `--ds-brand-*` con el color
  // que haya configurado la institución.
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { base } from '$app/paths';
  // El orden importa: `tokens.css` es copia de InnoTech y `outreach.css` lo
  // que este proyecto agrega encima.
  import '$lib/ds/tokens.css';
  import '$lib/ds/outreach.css';
  import { branding } from '$lib/branding.svelte';
  import { auth } from '$lib/auth.svelte';
  import { isEmbedded } from '$lib/session';
  import Navbar from '$lib/Navbar.svelte';

  let { children } = $props();

  const isLogin = $derived(page.url.pathname.startsWith(`${base}/login`));

  // Dentro del shell de InnoTech el marco lo pone él: ni navbar propio, ni
  // pantalla de acceso propia.
  let embedded = $state(false);

  onMount(() => {
    embedded = isEmbedded();
    auth.restore();
    branding.load();
    // Guardia: sin sesión no se ve nada más que el acceso. Embebida no aplica
    // — si el token del shell falla, el 401 lo resuelve allá.
    if (!embedded && !auth.isAuthenticated && !isLogin) goto(`${base}/login`);
  });
</script>

<svelte:head>
  <!-- El título sale del branding para que cada institución vea el suyo. -->
  <title>{branding.data.name}</title>
</svelte:head>

<!-- Embebida, el navbar lo pone el shell: dos navbars anidados serían un
     error de encuadre, no una decisión. Ver `lib/Navbar.svelte`. -->
{#if !isLogin && !embedded}
  <Navbar />
{/if}

{@render children()}

<style>
  :global(body) {
    margin: 0;
    font-family: var(--ds-font-family, system-ui), sans-serif;
    background: var(--ds-neutral-100, #f6f8fb);
    color: var(--ds-neutral-800, #1e293b);
  }
  :global(*) { box-sizing: border-box; }
</style>
