<!-- Copia de `@innotech/ui-svelte/components/table/Table.svelte` del monorepo
     de InnoTech. Sin cambios.

     La cabecera se pinta con `--ds-info-500` y texto blanco: es de allá, no una
     decisión de este proyecto. En esta aplicación esa familia la sobreescribe
     el **color secundario** de la institución (ver `lib/branding.svelte.ts`),
     así que la tabla se tiñe sola con la identidad de cada una. -->
<script lang="ts">
	/**
	 * @component Table
	 * Contenedor principal para tablas de datos InnoTech 2.0.
	 * Maneja el scroll horizontal y el estilo base del contenedor.
	 */
	interface Props {
		children?: import('svelte').Snippet;
		footer?: import('svelte').Snippet;
		class?: string;
		containerClass?: string;
	}

	let { children, footer, class: className = '', containerClass = '' }: Props = $props();
</script>

<div class="ds-table-container shadow-sm {containerClass}">
	<div class="ds-table-scroll">
		<table class="ds-table {className}">
			{#if children}
				{@render children()}
			{/if}
		</table>
	</div>
	{#if footer}
		<div class="ds-table-footer">
			{@render footer()}
		</div>
	{/if}
</div>

<style>
	.ds-table-container {
		width: 100%;
		border-radius: 12px;
		border: 1px solid #E2E8F0;
		background: white;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.ds-table-scroll {
		width: 100%;
		overflow-x: auto;
		scrollbar-width: thin;
		scrollbar-color: #E2E8F0 transparent;
	}

	.ds-table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
		min-width: 800px;
	}

	.ds-table-footer :global(.ds-pagination-footer) {
		border-top: 1px solid #E2E8F0;
	}
</style>
