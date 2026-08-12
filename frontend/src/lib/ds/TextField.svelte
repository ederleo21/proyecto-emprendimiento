<!-- Copia de `@innotech/ui-svelte/components/inputs/TextField.svelte` del monorepo de
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
		value?: any;
		type?: string;
		status?: 'Default' | 'Focused' | 'Success' | 'Warning' | 'Error';
		message?: string;
		size?: 'sm' | 'md' | 'lg';
		prefix?: Snippet;
		suffix?: Snippet;
		externalPrefix?: Snippet;
		externalSuffix?: Snippet;
		labelClass?: string;
		onchange?: (value: any) => void;
		oninput?: (value: any) => void;
		class?: string;
		[key: string]: any;
	}

	let { 
		label = '', 
		labelClass = '',
		placeholder = '', 
		value = $bindable(), 
		type = 'text', 
		status = 'Default', 
		message = '', 
		size = 'md', 
		prefix, 
		suffix,
		externalPrefix,
		externalSuffix,
		id = `tf-${Math.random().toString(36).substring(2, 9)}`,
		class: customClass = '',
		onchange,
		oninput,
		...rest
	}: Props = $props();

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
		const target = event.currentTarget as HTMLInputElement;
		value = target.value;
		oninput?.(target.value);
		onchange?.(target.value);
	}
</script>

<div class="ds-input-container {customClass}">
	{#if label}
		<label class="ds-field-label BodyM {labelClass}" for={id}>{label}</label>
	{/if}

	<div class="ds-field {activeStatus.toLowerCase()} {size} 
		{prefix ? 'has-prefix' : ''} 
		{suffix ? 'has-suffix' : ''} 
		{externalPrefix ? 'has-external-prefix' : ''} 
		{externalSuffix ? 'has-external-suffix' : ''}"
	>
		{#if externalPrefix}
			<div class="ds-external-prefix">{@render externalPrefix()}</div>
		{/if}

		{#if prefix}
			<div class="ds-prefix">
				{@render prefix()}
			</div>
		{/if}

		<input 
			{id}
			{type} 
			{placeholder} 
			bind:value 
			class="ds-input" 
			oninput={handleInput}
			onfocus={() => isFocused = true}
			onblur={() => isFocused = false}
			onwheel={(e) => { if (type === 'number') e.preventDefault() }}
			{...rest}
		/>

		{#if suffix}
			<div class="ds-suffix">
				{@render suffix()}
			</div>
		{/if}

		{#if externalSuffix}
			<div class="ds-external-suffix">{@render externalSuffix()}</div>
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
