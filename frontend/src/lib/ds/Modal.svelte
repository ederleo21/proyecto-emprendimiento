<!-- Copia de `@innotech/ui-svelte/components/Modal.svelte` del monorepo de
     InnoTech. Sin cambios.

     Reemplaza al que estaba hecho acá, que era una versión reducida sin
     animación. Este trae las transiciones de entrada y salida, los tamaños
     `xl` y `full`, y el `body` como snippet aparte de `children`. -->
<script module lang="ts">
	// Contador COMPARTIDO entre todas las instancias de Modal — si dos modales
	// están abiertos a la vez (o uno cierra en el mismo instante que otro abre,
	// como al confirmar una excepción de Crédito Académico), cada uno capturaba
	// su propio `prev` de forma independiente. En orden no-LIFO (ej. el primero
	// en abrir es el primero en cerrar, mientras el segundo sigue abierto), el
	// cierre del primero pisaba `overflow` con su prev ANTES de que cerrara el
	// segundo, y el cierre del segundo terminaba dejando 'hidden' fijo aunque
	// ya no quedara ningún modal abierto — la página entera (tablas incluidas)
	// se quedaba sin poder hacer scroll. Con un contador, solo el modal que
	// hizo el ÚLTIMO lock restaura el valor original.
	let modalLockCount = 0;
	let modalPrevOverflow = '';
</script>

<script lang="ts">
	import { fade, scale } from 'svelte/transition';
	import { onMount } from 'svelte';
	import Icon from './Icon.svelte';
	import type { Snippet } from 'svelte';

	// Acción portal robusta: anexa el nodo al <body> cuando el action
	// se inicializa (DESPUÉS de que Svelte gestiona las transiciones).
	function portal(node: HTMLElement) {
		// Guardamos posición original para limpiar correctamente
		const anchor = document.createComment('portal-anchor');
		node.parentNode?.insertBefore(anchor, node);
		document.body.appendChild(node);

		// Notificar al shell principal si estamos en un iframe
		if (window !== window.parent) {
			window.parent.postMessage({ type: 'INNOTECH_MODAL_OPEN' }, '*');
		}

		return {
			destroy() {
				if (document.body.contains(node)) {
					document.body.removeChild(node);
				}
				anchor.parentNode?.removeChild(anchor);

				// Notificar al shell principal si estamos en un iframe
				if (window !== window.parent) {
					window.parent.postMessage({ type: 'INNOTECH_MODAL_CLOSE' }, '*');
				}
			}
		};
	}

	interface Props {
		open?: boolean;
		title?: string;
		description?: string;
		icon?: string; // Icon name for the header
		size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
		showClose?: boolean;
		closeOnOutsideClick?: boolean;
		header?: Snippet;
		body?: Snippet;
		children?: Snippet;
		footer?: Snippet;
		id?: string;
		class?: string;
		onclose?: () => void;
		onClose?: () => void;
	}

	let {
		open = $bindable(false),
		title = '',
		description = '',
		icon = '',
		size = 'md',
		showClose = true,
		closeOnOutsideClick = true,
		header,
		body,
		children,
		footer,
		id = `modal-${Math.random().toString(36).substring(2, 9)}`,
		class: customClass = '',
		onclose,
		onClose
	}: Props = $props();

	let resolvedBody = $derived(children ?? body);
	let resolvedOnClose = $derived(onclose ?? onClose);

	// Bloquea el scroll del fondo mientras el modal está abierto: el contenido
	// del modal scrollea internamente (.ds-modal-body), la página no. Usa un
	// contador compartido (`modalLockCount`) para soportar modales anidados o
	// que se abren/cierran fuera de orden — ver comentario en <script module>.
	$effect(() => {
		if (typeof document === 'undefined' || !open) return;
		if (modalLockCount === 0) {
			modalPrevOverflow = document.body.style.overflow;
			document.body.style.overflow = 'hidden';
		}
		modalLockCount++;
		return () => {
			modalLockCount--;
			if (modalLockCount === 0) {
				document.body.style.overflow = modalPrevOverflow;
			}
		};
	});

	function handleClose() {
		open = false;
		resolvedOnClose?.();
	}

	function handleBackdropClick(e: MouseEvent) {
		if (closeOnOutsideClick && e.target === e.currentTarget) {
			handleClose();
		}
	}

	const sizeClasses = {
		sm: 'max-w-md',
		md: 'max-w-2xl',
		lg: 'max-w-4xl',
		xl: 'max-w-6xl',
		full: 'max-w-[95vw]'
	};
</script>

{#if open}
	<div 
		use:portal
		class="ds-modal-root"
		{id}
		role="dialog"
		aria-modal="true"
		aria-labelledby={title ? `${id}-title` : undefined}
		transition:fade={{ duration: 150 }}
	>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="ds-modal-backdrop" onclick={handleBackdropClick}>
			<div 
				class="ds-modal-content {sizeClasses[size]} {customClass}"
				in:scale={{ start: 0.98, duration: 200, opacity: 0 }}
			>
				{#if header}
					<header class="ds-modal-header">
						{#if showClose}
							<button class="ds-modal-close-abs" onclick={handleClose} aria-label="Cerrar">
								<Icon name="design-system/close" size="md" />
							</button>
						{/if}
						{@render header()}
					</header>
				{:else if title}
					<header class="ds-modal-header">
						<div class="ds-modal-header-left">
							{#if icon}
								<div class="ds-modal-icon-header">
									<Icon name={icon} size="lg" class="text-ds-info-500" />
								</div>
							{/if}
							<div class="ds-modal-title-group">
								<h6 class="ds-modal-title HeadingsH6" id="{id}-title">{title}</h6>
								{#if description}
									<p class="ds-modal-description SubheadingXS">{description}</p>
								{/if}
							</div>
						</div>

						{#if showClose}
							<div class="ds-modal-header-right">
								<button class="ds-modal-close-btn" onclick={handleClose} aria-label="Cerrar">
									<Icon name="design-system/close" size="md" />
								</button>
							</div>
						{/if}
					</header>
				{/if}

				<div class="ds-modal-body custom-scrollbar">
					{@render resolvedBody?.()}

					{#if footer}
						<footer class="ds-modal-footer">
							<div class="ds-modal-footer-inner">
								{@render footer()}
							</div>
						</footer>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.ds-modal-root {
		position: fixed;
		inset: 0;
		z-index: 9999;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 24px;
	}

	.ds-modal-backdrop {
		position: absolute;
		inset: 0;
		background: rgba(15, 23, 42, 0.4);
		backdrop-filter: blur(8px);
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
	}

	.ds-modal-content {
		position: relative;
		width: 100%;
		background: #FFFFFF;
		border-radius: 20px;
		display: flex;
		flex-direction: column;
		max-height: 90vh;
		box-shadow: 0 40px 80px -15px rgba(0, 0, 0, 0.15);
		border: 1px solid #F1F5F9;
		overflow: hidden;
	}

	.ds-modal-close-abs, .ds-modal-close-btn {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		border: none;
		background: transparent;
		color: #94A3B8;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.2s;
	}

	.ds-modal-close-abs {
		position: absolute;
		top: 40px;
		right: 40px;
		z-index: 10;
	}

	.ds-modal-close-abs:hover, .ds-modal-close-btn:hover {
		background: #F1F5F9;
		color: #0F172A;
		transform: rotate(90deg);
	}

	.ds-modal-header {
		padding: 40px 40px 24px 40px;
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 24px;
		flex-shrink: 0;
	}

	.ds-modal-header-left {
		display: flex;
		align-items: center;
		gap: 20px;
		flex: 1;
	}

	.ds-modal-icon-header {
		/*width: 56px;
		height: 56px;
		border-radius: 12px;
		background: #EBF5FF;*/
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.ds-modal-title-group {
		display: flex;
		flex-direction: column;
		gap: 4px;
		flex: 1;
	}

	.ds-modal-title {
		color: #1E293B;
		font-family: var(--ds-font-family);
		/*font-size: 22px;
		font-weight: 800;
		letter-spacing: -0.02em;*/
		margin: 0;
		
	}

	.ds-modal-description {
		color: #64748B;
		font-family: var(--ds-font-family);
		/*font-size: 14px;*/
		font-weight: 500;
		margin: 0;
	}

	.ds-modal-body {
		padding: 0 40px 40px 40px;
		overflow-y: auto;
		/* Evita que el scroll del modal propague al fondo y habilita scroll suave en iOS */
		overscroll-behavior: contain;
		-webkit-overflow-scrolling: touch;
		touch-action: auto;
		flex: 1;
		font-size: 15px;
		color: #475569;
		line-height: 1.6;
	}

	.ds-modal-footer {
		margin-top: 24px;
	}

	.ds-modal-footer-inner {
		display: flex;
		justify-content: flex-start; /* Matches image bottom layout */
		gap: 16px;
		width: 100%;
	}

	/* Max-width utilities */
	.max-w-md { max-width: 448px; }
	.max-w-2xl { max-width: 600px; }
	.max-w-4xl { max-width: 800px; }
	.max-w-6xl { max-width: 1000px; }

	.custom-scrollbar::-webkit-scrollbar {
		width: 5px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: transparent;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: #E2E8F0;
		border-radius: 10px;
	}

	@media (max-width: 640px) {
		.ds-modal-header, .ds-modal-body {
			padding: 24px;
		}
		.ds-modal-root {
			padding: 12px;
		}
		.ds-modal-content {
			border-radius: 24px 24px 0 0;
			/*margin-top: auto;*/
			max-height: 85vh;
		}
	}
</style>
