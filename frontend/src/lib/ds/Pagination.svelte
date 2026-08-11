<!-- Copia de `@innotech/ui-svelte/components/Pagination.svelte` del monorepo de
     InnoTech. Se trae tal cual para que estas pantallas se vean igual que las
     de allá y para dejar de mantener una versión casera peor.

     Único cambio: los nombres de icono (`arrows/arrow-left-2` y
     `arrows/arrow-right-2` no existen en nuestro `Icon`; se usan los
     chevrones equivalentes).

     Si InnoTech mejora el suyo, se vuelve a copiar — mismo trato que `core/`
     en el backend y que `tokens.css`. -->
<script lang="ts">
	import Icon from './Icon.svelte';

	/**
	 * @component Pagination
	 * Componente de paginación InnoTech 2.0.
	 * Proporciona controles de navegación y estadísticas de registros.
	 */
	interface Props {
		currentPage?: number;
		totalPages?: number;
		totalItems?: number;
		pageSize?: number;
		variant?: 'full' | 'simple' | 'minimal';
		onPageChange?: (page: number) => void;
	}

	let { 
		currentPage = 1, 
		totalPages = 1, 
		totalItems = 0, 
		pageSize = 10,
		variant = 'full',
		onPageChange 
	}: Props = $props();

	// Cálculos reactivos para las estadísticas
	const rangeStart = $derived(totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1);
	const rangeEnd = $derived(Math.min(currentPage * pageSize, totalItems));
	const visibleCount = $derived(totalItems === 0 ? 0 : Math.max(0, rangeEnd - rangeStart + 1));

	/** Lista de páginas a mostrar con ellipses cuando hay muchas. */
	const pageNumbers = $derived.by<(number | 'dots-left' | 'dots-right')[]>(() => {
		const total = Math.max(1, totalPages);
		const current = Math.min(Math.max(1, currentPage), total);
		const out: (number | 'dots-left' | 'dots-right')[] = [];

		if (total <= 7) {
			for (let i = 1; i <= total; i++) out.push(i);
			return out;
		}

		out.push(1);
		if (current > 3) out.push('dots-left');

		const start = Math.max(2, current - 1);
		const end = Math.min(total - 1, current + 1);
		for (let i = start; i <= end; i++) out.push(i);

		if (current < total - 2) out.push('dots-right');
		out.push(total);
		return out;
	});

	function goToPage(page: number) {
		if (page < 1 || page > totalPages || page === currentPage) return;
		onPageChange?.(page);
	}
</script>

<div class="ds-pagination-footer" class:minimal={variant === 'minimal'}>
	{#if variant === 'full'}
		<div class="ds-pagination-stats">
			<span class="label">Mostrando</span>
			<span class="value">{visibleCount}</span>
			<span class="label">de</span>
			<span class="value">{totalItems}</span>
			<span class="label">registros</span>
		</div>
	{/if}

	<div class="ds-pagination-controls">
		<button
			class="pager-arrow"
			disabled={currentPage === 1}
			onclick={() => goToPage(currentPage - 1)}
			aria-label="Página anterior"
		>
			<Icon name="arrows/chevron-left" size="sm" />
		</button>

		{#each pageNumbers as p}
			{#if p === 'dots-left' || p === 'dots-right'}
				<span class="pager-ellipsis" aria-hidden="true">…</span>
			{:else}
				<button
					class="pager-number"
					class:active={p === currentPage}
					onclick={() => goToPage(p)}
					aria-label={`Ir a la página ${p}`}
					aria-current={p === currentPage ? 'page' : undefined}
				>
					{p}
				</button>
			{/if}
		{/each}

		<button
			class="pager-arrow"
			disabled={currentPage === totalPages}
			onclick={() => goToPage(currentPage + 1)}
			aria-label="Página siguiente"
		>
			<Icon name="arrows/chevron-right" size="sm" />
		</button>
	</div>
</div>

<style>
	.ds-pagination-footer {
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		align-items: center;
		padding: 0 32px;
		width: 100%;
		height: 65px;
		background: transparent;
		box-sizing: border-box;
		user-select: none;
	}

	/* Alineación central para variantes que no tienen stats */
	.ds-pagination-footer.minimal {
		justify-content: center;
		background: transparent;
		border-top: none;
	}

	.ds-pagination-stats {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 6px;
	}

	.ds-pagination-controls {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 6px;
	}

	/* Chevrones (anterior / siguiente) — solo icono, sin contenedor. */
	.pager-arrow {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: transparent;
		border: none;
		outline: none;
		color: var(--ds-neutral-600, #64748B);
		cursor: pointer;
		transition: color 0.15s ease;
		padding: 0;
	}
	.pager-arrow:hover:not(:disabled) {
		color: var(--ds-brand-600, #000066);
	}
	.pager-arrow:focus,
	.pager-arrow:focus-visible {
		outline: none;
		box-shadow: none;
	}
	.pager-arrow:disabled {
		cursor: not-allowed;
		opacity: 0.4;
	}

	/* Números clickeables. */
	.pager-number {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 32px;
		height: 32px;
		padding: 0 8px;
		border-radius: 50%;
		background: transparent;
		border: none;
		color: var(--ds-neutral-700, #1E293B);
		font-family: 'Inter', sans-serif;
		font-weight: 600;
		font-size: 13px;
		cursor: pointer;
		transition: all 0.15s ease;
	}
	.pager-number:hover:not(.active) {
		background: var(--ds-neutral-100, #F8FAFC);
		color: var(--ds-brand-600, #000066);
	}
	.pager-number.active {
		background: var(--ds-info-600, #1A85FF);
		color: white;
		cursor: default;
	}

	.pager-ellipsis {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 24px;
		height: 32px;
		color: var(--ds-neutral-500, #94A3B8);
		font-weight: 600;
		font-size: 13px;
		user-select: none;
	}

	.label {
		font-family: 'Inter', sans-serif;
		font-weight: 600;
		font-size: 13px;
		color: var(--ds-neutral-500, #94A3B8);
	}

	.value {
		font-family: 'Inter', sans-serif;
		font-weight: 700;
		font-size: 13px;
		color: var(--ds-neutral-700, #1E293B);
	}

	/* Responsive tweaks */
	@media (max-width: 640px) {
		.ds-pagination-footer {
			flex-direction: column;
			height: auto;
			padding: 16px;
			gap: 16px;
		}
		
		.ds-pagination-stats {
			order: 2;
		}
	}
</style>
