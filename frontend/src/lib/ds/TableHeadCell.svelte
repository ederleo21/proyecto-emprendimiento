<!-- Copia de `@innotech/ui-svelte/components/table/TableHeadCell.svelte` del monorepo
     de InnoTech. Sin cambios.

     La cabecera se pinta con `--ds-info-500` y texto blanco: es de allá, no una
     decisión de este proyecto. En esta aplicación esa familia la sobreescribe
     el **color secundario** de la institución (ver `lib/branding.svelte.ts`),
     así que la tabla se tiñe sola con la identidad de cada una. -->
<script lang="ts">
	/**
	 * @component TableHeadCell
	 * Celda de cabecera con soporte para ordenamiento.
	 */
	interface Props {
		children?: import('svelte').Snippet;
		class?: string;
		style?: string;
		/** Ancho de la columna (CSS: '14%', '120px'...). Con table-layout:fixed reparte el ancho. */
		width?: string;
		sortable?: boolean;
		sortDirection?: 'asc' | 'desc' | 'none';
		onsort?: (direction: 'asc' | 'desc' | 'none') => void;
		align?: 'left' | 'center' | 'right';
		/** Cabeceras agrupadas: un título que abarca varias columnas. */
		colspan?: number;
		/** Cabeceras agrupadas: una columna que abarca las dos filas del thead. */
		rowspan?: number;
	}

	let {
		children,
		class: className = '',
		style = '',
		width = '',
		sortable = false,
		sortDirection = 'none',
		onsort,
		align = 'left',
		colspan,
		rowspan
	}: Props = $props();

	const cellStyle = $derived(width ? `width:${width};${style}` : style);

	function handleSort() {
		if (!sortable) return;
		const nextDirection = sortDirection === 'none' ? 'asc' : sortDirection === 'asc' ? 'desc' : 'none';
		if (onsort) onsort(nextDirection);
	}
</script>

<th 
	class="ds-th SubheadingSM {className}" 
	class:sortable={sortable}
	class:text-left={align === 'left'}
	class:text-center={align === 'center'}
	class:text-right={align === 'right'}
	onclick={handleSort}
	{colspan}
	{rowspan}
	style={cellStyle}
>
	<div class="header-content" class:justify-center={align === 'center'} class:justify-end={align === 'right'}>
		{#if children}
			{@render children()}
		{/if}
		
		{#if sortable}
			<svg width="16" height="12" viewBox="0 0 16 12" fill="none" class="sort-icon" class:active={sortDirection !== 'none'}>
				<!-- Down arrow if desc, Up arrow if asc, both if none -->
				{#if sortDirection === 'asc'}
					<path d="M4 4L8 0L12 4H4Z" fill="currentColor"/>
					<path d="M4 8L8 12L12 8H4Z" fill="currentColor" opacity="0.1"/>
				{:else if sortDirection === 'desc'}
					<path d="M4 4L8 0L12 4H4Z" fill="currentColor" opacity="0.1"/>
					<path d="M4 8L8 12L12 8H4Z" fill="currentColor"/>
				{:else}
					<path d="M4 4L8 0L12 4H4Z" fill="currentColor" opacity="0.3"/>
					<path d="M4 8L8 12L12 8H4Z" fill="currentColor" opacity="0.3"/>
				{/if}
			</svg>
		{/if}
	</div>
</th>

<style>
	.ds-th {
		padding: 16px 24px;
		/* Hereda color del contenedor (.ds-table-head) — permite tematizar */
		color: inherit;
		white-space: nowrap;
		user-select: none;
	}

	.ds-th.sortable {
		cursor: pointer;
	}

	/* Sin cambio de color en hover — el cursor pointer ya indica que es clickeable.
	   Antes hardcodeaba color oscuro, ilegible sobre fondos coloridos (celeste). */
	.ds-th.sortable:hover {
		color: inherit;
	}

	.header-content {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.header-content.justify-center {
		justify-content: center;
	}

	.header-content.justify-end {
		justify-content: flex-end;
	}

	.text-left { text-align: left; }
	.text-center { text-align: center; }
	.text-right { text-align: right; }

	.sort-icon {
		transition: all 0.2s;
		color: #94A3B8;
	}

	.sort-icon.active {
		color: #000080;
	}
</style>
