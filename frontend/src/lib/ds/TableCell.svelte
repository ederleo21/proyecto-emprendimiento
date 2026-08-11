<!-- Copia de `@innotech/ui-svelte/components/table/TableCell.svelte` del monorepo
     de InnoTech. Sin cambios.

     La cabecera se pinta con `--ds-info-500` y texto blanco: es de allá, no una
     decisión de este proyecto. En esta aplicación esa familia la sobreescribe
     el **color secundario** de la institución (ver `lib/branding.svelte.ts`),
     así que la tabla se tiñe sola con la identidad de cada una. -->
<script lang="ts">
	/**
	 * @component TableCell
	 * Celda de datos individual (TD).
	 */
	interface Props {
		children?: import('svelte').Snippet;
		class?: string;
		align?: 'left' | 'center' | 'right';
		[key: string]: any;
	}

	let { children, class: className = '', align = 'left', ...rest }: Props = $props();
</script>

<td {...rest} class="ds-td BodyS {className}" class:text-left={align === 'left'} class:text-center={align === 'center'} class:text-right={align === 'right'}>
	{#if children}
		{@render children()}
	{/if}
</td>

<style>
	.ds-td {
		padding: 16px 24px;
		color: #292D32;
		vertical-align: middle;
	}

	.text-left { text-align: left; }
	.text-center { text-align: center; }
	.text-right { text-align: right; }
</style>
