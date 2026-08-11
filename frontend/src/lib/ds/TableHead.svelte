<!-- Copia de `@innotech/ui-svelte/components/table/TableHead.svelte` del monorepo
     de InnoTech. Sin cambios.

     La cabecera se pinta con `--ds-info-500` y texto blanco: es de allá, no una
     decisión de este proyecto. En esta aplicación esa familia la sobreescribe
     el **color secundario** de la institución (ver `lib/branding.svelte.ts`),
     así que la tabla se tiñe sola con la identidad de cada una. -->
<script lang="ts">
	/**
	 * @component TableHead
	 * Wrapper para la sección <thead> de una tabla InnoTech.
	 */
	interface Props {
		children?: import('svelte').Snippet;
		class?: string;
	}

	let { children, class: className = '' }: Props = $props();
</script>

<thead class="ds-table-head {className}">
	{#if children}
		{@render children()}
	{/if}
</thead>

<style>
	.ds-table-head {
		background: var(--ds-info-500, #3399FF);
		color: white;
	}
	/* Pintar explícitamente cada <th> para evitar que el fondo del row-group
	   no traspase en ciertos contextos de stacking (overflow:hidden/clip en ancestros). */
	.ds-table-head :global(.ds-th) {
		background-color: var(--ds-info-500, #3399FF);
		color: white;
	}
	.ds-table-head :global(.sort-icon) {
		color: rgba(255, 255, 255, 0.7);
	}
	.ds-table-head :global(.sort-icon.active) {
		color: white;
	}
</style>
