<!-- Copia de `@innotech/ui-svelte/components/Tooltip.svelte`. Sin cambios.
     Lo necesita `RowActions`. -->
<script lang="ts">
	/**
	 * InnoTech 2.0 Premium Tooltip Component
	 * Based on InnoTech 2.0.30.03 Design System
	 *
	 * Usa position:fixed + portal para escapar cualquier overflow:hidden/auto
	 * del árbol de contenedores (scroll panels, cards, etc.)
	 */
	interface Props {
		title?: string;
		content?: string;
		position?: 'top' | 'bottom' | 'left' | 'right';
		variant?: 'dark' | 'light';
		children?: import('svelte').Snippet;
		visible?: boolean;
	}

	let {
		title = '',
		content = '',
		position = 'top',
		variant = 'dark',
		children,
		visible = false
	}: Props = $props();

	let isHovered = $state(false);
	let show = $derived(visible || isHovered);
	let wrapperEl = $state<HTMLElement | null>(null);

	// Acción portal: mueve el tooltip a document.body y lo posiciona
	// con coordenadas fijas respecto al viewport, escapando cualquier
	// contenedor con overflow:hidden o overflow:auto.

	/** Centra el globo sobre el elemento sin dejar que se salga de la pantalla.
	 *  Un elemento pegado al borde derecho (la última acción de una fila) dejaba
	 *  el texto cortado; aquí el globo se corre hacia adentro y la flecha se
	 *  desplaza lo mismo para seguir apuntando al elemento. */
	const MARGEN_VIEWPORT = 8;
	function centrarHorizontal(node: HTMLElement, r: DOMRect) {
		const centro = r.left + r.width / 2;
		const mitad = node.offsetWidth / 2;
		const min = mitad + MARGEN_VIEWPORT;
		const max = window.innerWidth - mitad - MARGEN_VIEWPORT;
		const x = max < min ? centro : Math.min(Math.max(centro, min), max);
		node.style.left = `${x}px`;
		node.style.setProperty('--ds-tt-arrow', `${centro - x}px`);
	}

	function portal(node: HTMLElement) {
		function place() {
			if (!wrapperEl) return;
			const r = wrapperEl.getBoundingClientRect();
			node.style.position = 'fixed';
			node.style.zIndex = '9999';
			// Resetear posición heredada de las clases CSS
			node.style.top = 'auto';
			node.style.bottom = 'auto';
			node.style.left = 'auto';
			node.style.right = 'auto';

			// La posición vive en --ds-tt-pos: la animación la compone con scale()
			// sin pisarla (antes el keyframe forzaba translateX(-50%) en todas).
			switch (position) {
				case 'top':
					node.style.bottom = `${window.innerHeight - r.top + 12}px`;
					centrarHorizontal(node, r);
					node.style.setProperty('--ds-tt-pos', 'translateX(-50%)');
					break;
				case 'bottom':
					node.style.top = `${r.bottom + 12}px`;
					centrarHorizontal(node, r);
					node.style.setProperty('--ds-tt-pos', 'translateX(-50%)');
					break;
				case 'left':
					node.style.top = `${r.top + r.height / 2}px`;
					node.style.right = `${window.innerWidth - r.left + 12}px`;
					node.style.setProperty('--ds-tt-pos', 'translateY(-50%)');
					break;
				case 'right':
					node.style.top = `${r.top + r.height / 2}px`;
					node.style.left = `${r.right + 12}px`;
					node.style.setProperty('--ds-tt-pos', 'translateY(-50%)');
					break;
			}
			node.style.transform = 'var(--ds-tt-pos)';
		}

		document.body.appendChild(node);
		requestAnimationFrame(place);

		return {
			destroy() {
				if (node.isConnected) node.remove();
			}
		};
	}
</script>

<div
	bind:this={wrapperEl}
	class="ds-tooltip-wrapper"
	role="presentation"
	onmouseenter={() => isHovered = true}
	onmouseleave={() => isHovered = false}
>
	{@render children?.()}

	{#if show}
		<div use:portal class="ds-tooltip ds-tooltip-{position} ds-tooltip-{variant}">
			<div class="ds-tooltip-content">
				{#if title}
					<span class="ds-tooltip-title">{title}</span>
				{/if}
				{#if content}
					<span class="ds-tooltip-text">{content}</span>
				{/if}
			</div>
			<div class="ds-tooltip-arrow"></div>
		</div>
	{/if}
</div>

<style>
	.ds-tooltip-wrapper {
		position: relative;
		display: inline-block;
	}

	.ds-tooltip {
		position: absolute; /* sobreescrito a fixed por la acción portal */
		z-index: 9999;
		width: max-content;
		max-width: 280px;
		display: flex;
		flex-direction: column;
		align-items: center;
		pointer-events: none;
		animation: ds-tooltip-in 0.15s ease-out forwards;
	}

	@keyframes ds-tooltip-in {
		from { opacity: 0; transform: var(--ds-tt-pos, translateX(-50%)) scale(0.97); }
		to   { opacity: 1; transform: var(--ds-tt-pos, translateX(-50%)) scale(1); }
	}

	/* Padding/typography reducidos: el tooltip es una guía rápida, no un panel.
	   Cuando se pasa solo `title` queda compacto; agregar `content` lo hace mas
	   alto pero sin volverse panel. */
	.ds-tooltip-content {
		padding: 6px 10px;
		border-radius: 6px;
		display: flex;
		flex-direction: column;
		gap: 2px;
		box-shadow: 0 6px 16px -4px rgba(0, 0, 64, 0.18);
	}

	/* Dark Variant */
	.ds-tooltip-dark .ds-tooltip-content {
		background-color: rgba(15, 23, 42, 0.95);
		border: 1px solid rgba(15, 23, 42, 0.95);
	}
	.ds-tooltip-dark .ds-tooltip-title {
		color: #FFFFFF;
		font-weight: 600;
		font-size: 12px;
		line-height: 1.3;
	}
	.ds-tooltip-dark .ds-tooltip-text {
		color: rgba(203, 213, 225, 1);
		font-size: 11px;
		line-height: 1.3;
	}

	/* Light Variant */
	.ds-tooltip-light .ds-tooltip-content {
		background-color: #FFFFFF;
		border: 1px solid #E2E8F0;
	}
	.ds-tooltip-light .ds-tooltip-title {
		color: rgba(15, 23, 42, 1);
		font-weight: 600;
		font-size: 12px;
		line-height: 1.3;
	}
	.ds-tooltip-light .ds-tooltip-text {
		color: rgba(100, 116, 139, 1);
		font-size: 11px;
		line-height: 1.3;
	}

	/* Arrow */
	.ds-tooltip-arrow {
		width: 0;
		height: 0;
		border-style: solid;
		position: absolute;
	}

	.ds-tooltip-top .ds-tooltip-arrow {
		bottom: -5px;
		/* --ds-tt-arrow compensa el corrimiento del globo contra el borde. */
		left: calc(50% + var(--ds-tt-arrow, 0px));
		transform: translateX(-50%);
		border-width: 5px 6px 0 6px;
	}
	.ds-tooltip-dark.ds-tooltip-top .ds-tooltip-arrow  { border-color: rgba(0, 0, 64, 1) transparent transparent transparent; }
	.ds-tooltip-light.ds-tooltip-top .ds-tooltip-arrow { border-color: #FFFFFF transparent transparent transparent; }

	.ds-tooltip-bottom .ds-tooltip-arrow {
		top: -5px;
		left: calc(50% + var(--ds-tt-arrow, 0px));
		transform: translateX(-50%);
		border-width: 0 6px 5px 6px;
	}
	.ds-tooltip-dark.ds-tooltip-bottom .ds-tooltip-arrow  { border-color: transparent transparent rgba(0, 0, 64, 1) transparent; }
	.ds-tooltip-light.ds-tooltip-bottom .ds-tooltip-arrow { border-color: transparent transparent #FFFFFF transparent; }

	.ds-tooltip-left .ds-tooltip-arrow {
		right: -5px;
		top: 50%;
		transform: translateY(-50%);
		border-width: 5px 0 5px 5px;
	}
	.ds-tooltip-dark.ds-tooltip-left .ds-tooltip-arrow  { border-color: transparent transparent transparent rgba(0, 0, 64, 1); }
	.ds-tooltip-light.ds-tooltip-left .ds-tooltip-arrow { border-color: transparent transparent transparent #FFFFFF; }

	.ds-tooltip-right .ds-tooltip-arrow {
		left: -5px;
		top: 50%;
		transform: translateY(-50%);
		border-width: 5px 5px 5px 0;
	}
	.ds-tooltip-dark.ds-tooltip-right .ds-tooltip-arrow  { border-color: transparent rgba(0, 0, 64, 1) transparent transparent; }
	.ds-tooltip-light.ds-tooltip-right .ds-tooltip-arrow { border-color: transparent #FFFFFF transparent transparent; }
</style>
