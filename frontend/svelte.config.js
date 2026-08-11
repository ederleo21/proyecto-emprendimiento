import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// Prefijo de las rutas. Vacío suelto (`/proyectos`), y con prefijo cuando esto
// se sirve embebido en el shell de InnoTech (`/outreach/proyectos`), igual que
// hace `academic-sv` con `paths.base = '/academic'`.
//
// Va por variable de entorno y no fijo, porque las dos formas de correr son
// legítimas: suelto para desarrollar sin levantar InnoTech, embebido en el
// ecosistema. SvelteKit lo exige empezando por `/` y sin `/` final.
const basePath = (process.env.BASE_PATH ?? '').replace(/\/$/, '');

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    paths: {
      base: basePath,
    },
  },
};

export default config;
