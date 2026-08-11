// `sveltekit` viene de `@sveltejs/kit/vite`, NO de `@sveltejs/vite-plugin-svelte`
// — ese paquete solo exporta el plugin de Svelte a secas.
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

// De dónde se piden los assets. Suelto es la raíz; embebido en el shell de
// InnoTech es `/mfe/outreach/`, que es el prefijo bajo el que su Nginx sirve
// cada micro-frontend. Ojo que no coincide con `BASE_PATH`, el de las rutas:
// en ese ecosistema son dos prefijos distintos a propósito (`academic-sv` usa
// `/mfe/academic/` para assets y `/academic` para rutas).
const assetBase = process.env.ASSET_BASE ?? '/';

export default defineConfig({
  base: assetBase,
  plugins: [sveltekit()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Embebido, el shell lo carga desde otro origin: sin CORS el navegador
    // bloquea los módulos que pide el iframe en desarrollo.
    cors: true,
    // El bind-mount de Docker en Windows no propaga eventos de filesystem:
    // sin polling, el hot reload no se entera de los cambios.
    watch: { usePolling: true },
  },
});
