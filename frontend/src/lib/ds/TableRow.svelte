<!-- Copia de `@innotech/ui-svelte/components/table/TableRow.svelte` del monorepo
     de InnoTech. Sin cambios.

     La cabecera se pinta con `--ds-info-500` y texto blanco: es de allá, no una
     decisión de este proyecto. En esta aplicación esa familia la sobreescribe
     el **color secundario** de la institución (ver `lib/branding.svelte.ts`),
     así que la tabla se tiñe sola con la identidad de cada una. -->
<script lang="ts">
	/**
	 * @component TableRow
	 * Fila individual para la tabla InnoTech.
	 */
	interface Props {
		children?: import('svelte').Snippet;
		class?: string;
		isAlt?: boolean;
		hoverable?: boolean;
		[key: string]: any;
	}

	let { children, class: className = '', isAlt = false, hoverable = true, ...rest }: Props = $props();
</script>

<tr 
	class="ds-table-row {className}" 
	class:is-alt={isAlt}
	class:hoverable={hoverable}
	{...rest}
>
	{#if children}
		{@render children()}
	{/if}
</tr>

<style>
	.ds-table-row {
		border-bottom: 1px solid #F1F5F9;
		transition: background-color 0.2s;
	}

	.ds-table-row.is-alt {
		background: #F8FAFC;
	}

	.ds-table-row.hoverable:hover {
		background-color: #F1F5F9;
	}

	/* Evitar sobreescribir fondo de cabecera si se usa dentro de TableHead.
	   Tambien desactivar el hover gris (rompia el header celeste). */
	:global(.ds-table-head) .ds-table-row,
	:global(.ds-table-head) .ds-table-row.hoverable:hover {
		border-bottom: 1px solid #E2E8F0;
		background: transparent;
	}
</style>
