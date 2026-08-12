<!-- Copia de `@innotech/ui-svelte/components/inputs/TextArea.svelte` del monorepo de
     InnoTech. Único cambio: la ruta del `Icon`, que acá vive en la misma
     carpeta.

     Reemplaza al que estaba hecho acá, que declaraba por su cuenta las
     clases `.ds-field` y `.ds-field-label`. Al traer el `global.css`
     completo esas clases pasaron a existir también allí, y el campo salía
     con doble borde. -->
<script lang="ts">
	import Icon from './Icon.svelte';
	import type { Snippet } from 'svelte';

	interface Props {
		label?: string;
		placeholder?: string;
		value?: string;
		status?: 'Default' | 'Focused' | 'Success' | 'Warning' | 'Error';
		message?: string;
		size?: 'sm' | 'md' | 'lg';
		rows?: number;
		autoGrow?: boolean;
		class?: string;
		onchange?: (value: string) => void;
		oninput?: (value: string) => void;
		[key: string]: any;
	}

	let {
		label = '',
		placeholder = '',
		value = $bindable(''),
		status = 'Default',
		message = '',
		size = 'md',
		rows = 3,
		autoGrow = false,
		id = `ta-${Math.random().toString(36).substring(2, 9)}`,
		class: customClass = '',
		onchange,
		oninput,
		...rest
	}: Props = $props();

	let taEl = $state<HTMLTextAreaElement | null>(null);
	let baseHeight = 0;

	$effect(() => {
		if (!autoGrow || !taEl) return;
		// Altura natural según `rows`, usada como mínimo.
		if (!baseHeight) baseHeight = taEl.clientHeight;
		value; // dependencia: recalcular cuando cambia el texto (ej. IA)
		taEl.style.height = 'auto';
		taEl.style.height = `${Math.max(taEl.scrollHeight, baseHeight)}px`;
	});

	const statusColors: Record<string, string> = {
		Default: 'text-ds-neutral-500',
		Focused: 'text-ds-info-500',
		Success: 'text-ds-success-500',
		Warning: 'text-ds-warning-500',
		Error: 'text-ds-error-500'
	};

	const statusIcons: Record<string, string> = {
		Success: 'design-system/check',
		Warning: 'design-system/alert',
		Error: 'design-system/error'
	};

	let isFocused = $state(false);
	const activeStatus = $derived(isFocused ? 'Focused' : status);

	function handleInput(event: Event) {
		const target = event.currentTarget as HTMLTextAreaElement;
		value = target.value;
		oninput?.(target.value);
		onchange?.(target.value);
	}
</script>

<div class="ds-input-container {customClass}">
	{#if label}
		<label class="ds-field-label BodyM" for={id}>{label}</label>
	{/if}

	<div class="ds-field {activeStatus.toLowerCase()} {size} ds-textarea-container" class:autogrow={autoGrow}>
		<textarea
			bind:this={taEl}
			{id}
			{placeholder}
			bind:value
			{rows}
			class="ds-input ds-textarea"
			oninput={handleInput}
			onfocus={() => isFocused = true}
			onblur={() => isFocused = false}
			{...rest}
		></textarea>

		{#if !autoGrow}
			<div class="ds-textarea-resize-handle">
				<div class="ds-handle-line-1"></div>
				<div class="ds-handle-line-2"></div>
			</div>
		{/if}
	</div>

	{#if message}
		<div class="ds-message {status.toLowerCase()}">
			{#if statusIcons[status]}
				<Icon name={statusIcons[status]} size="sm" class="!{statusColors[status]}" />
			{/if}
			<span class="CaptionSM {statusColors[status]}">{message}</span>
		</div>
	{/if}
</div>

<style>
	/* Modo auto-crecer: el textarea se adapta al contenido, sin scroll ni
	   handle de resize manual. La altura la fija el $effect. */
	.ds-textarea-container.autogrow :global(.ds-textarea) {
		resize: none;
		overflow: hidden;
	}
</style>
