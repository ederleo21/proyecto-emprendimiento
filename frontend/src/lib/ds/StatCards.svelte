<!-- Copia de `@innotech/ui-svelte/components/StatCards.svelte` del monorepo de
     InnoTech. Se trae tal cual para que estas pantallas se vean igual que las
     de allá y para dejar de mantener una versión casera peor.

     Único cambio: ninguno.

     Si InnoTech mejora el suyo, se vuelve a copiar — mismo trato que `core/`
     en el backend y que `tokens.css`. -->
<script lang="ts">
	import Icon from './Icon.svelte';

	export interface StatItem {
		label: string;
		value: string | number;
		icon: string;
		color?: string;
		detail?: string;
	}

	interface Props {
		items: StatItem[];
		minWidth?: number;
	}

	let { items, minWidth = 200 }: Props = $props();
</script>

<div class="stats-grid" style="--stats-min: {minWidth}px">
	{#each items as s (s.label)}
		<div class="stat-card" style="--stat-color: var(--ds-{s.color ?? 'brand'}-500)">
			<div class="stat-content">
				<div class="stat-main">
					<div class="stat-icon-wrapper">
						<Icon name={s.icon} size="sm" />
					</div>
					<div class="stat-info">
						<span class="stat-label">{s.label}</span>
						<span class="stat-value">{s.value}</span>
					</div>
				</div>
				{#if s.detail}
					<div class="stat-footer">
						<span class="stat-detail">{s.detail}</span>
						<div class="stat-dot"></div>
					</div>
				{/if}
			</div>
		</div>
	{/each}
</div>

<style>
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(var(--stats-min, 200px), 1fr));
		gap: 16px;
		width: 100%;
	}
	.stat-card {
		background: #ffffff;
		border: 1px solid var(--ds-neutral-100);
		border-radius: 14px;
		overflow: hidden;
		transition: all 0.2s ease;
		min-width: 0;
	}
	.stat-content {
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.stat-main {
		display: flex;
		align-items: center;
		gap: 16px;
	}
	.stat-icon-wrapper {
		width: 40px;
		height: 40px;
		border-radius: 10px;
		background: color-mix(in srgb, var(--stat-color), transparent 90%);
		color: var(--stat-color);
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}
	.stat-info {
		display: flex;
		flex-direction: column;
		min-width: 0;
	}
	.stat-label {
		font-size: 11px;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--ds-neutral-400);
	}
	.stat-value {
		font-size: 28px;
		font-weight: 900;
		color: var(--ds-neutral-800);
		line-height: 1.1;
	}
	.stat-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-top: 12px;
		border-top: 1px dashed var(--ds-neutral-100);
	}
	.stat-detail {
		font-size: 10px;
		color: var(--ds-neutral-400);
		font-weight: 600;
	}
	.stat-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--stat-color);
	}
</style>
