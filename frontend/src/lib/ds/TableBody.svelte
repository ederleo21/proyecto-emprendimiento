<!-- Copia de `@innotech/ui-svelte/components/table/TableBody.svelte` del monorepo
     de InnoTech. Sin cambios.

     La cabecera se pinta con `--ds-info-500` y texto blanco: es de allá, no una
     decisión de este proyecto. En esta aplicación esa familia la sobreescribe
     el **color secundario** de la institución (ver `lib/branding.svelte.ts`),
     así que la tabla se tiñe sola con la identidad de cada una. -->
<script lang="ts">
	/**
	 * @component TableBody
	 * Wrapper para la sección <tbody> de una tabla InnoTech.
	 */
	interface Props {
		children?: import('svelte').Snippet;
		class?: string;
	}

	let { children, class: className = '' }: Props = $props();
</script>

<tbody class="ds-table-body {className}">
	{#if children}
		{@render children()}
	{/if}
</tbody>
