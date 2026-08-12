// Design system del proyecto.
//
// Los nombres y las props coinciden con `@innotech/ui-svelte` a propósito: el
// día que esto se integre al monorepo de InnoTech, la migración es cambiar
// este import por el del paquete y borrar la carpeta.
//
//   - import { Button, Modal } from '$lib/ds';
//   + import { Button, Modal } from '@innotech/ui-svelte';
//
// Solo existen los componentes que las pantallas usan. InnoTech tiene 48;
// construir los otros cuarenta "por si acaso" sería código muerto.
//
// Hay dos orígenes distintos, y conviene no confundirlos:
//
//   - **Hechos acá**, imitando la firma de InnoTech pero con una
//     implementación reducida a lo que las pantallas necesitan.
//   - **Copiados de allá** tal cual. Llevan la nota de procedencia en su
//     cabecera y no se les mete mano: si hace falta un cambio, se sube allá y
//     se vuelve a copiar.

// Hechos acá
export { default as Badge } from './Badge.svelte';
export { default as Button } from './Button.svelte';
export { default as Icon } from './Icon.svelte';

// Copiados de `@innotech/ui-svelte`
export { default as Pagination } from './Pagination.svelte';
export { default as ProgressBar } from './ProgressBar.svelte';
export { default as StatCards } from './StatCards.svelte';
export { default as ViewToggle } from './ViewToggle.svelte';

export { default as Checkbox } from './Checkbox.svelte';
export { default as ConfirmModal } from './ConfirmModal.svelte';
export { default as Modal } from './Modal.svelte';
export { default as StatusToggle } from './StatusToggle.svelte';
export { default as Switch } from './Switch.svelte';
export { default as RowActions, type RowAction } from './RowActions.svelte';
export { default as Select } from './Select.svelte';
export { default as TextArea } from './TextArea.svelte';
export { default as TextField } from './TextField.svelte';
export { default as Tooltip } from './Tooltip.svelte';

// Tabla, también de allá. Se usan juntos:
//   <Table><TableHead><TableRow><TableHeadCell>…
export { default as Table } from './Table.svelte';
export { default as TableBody } from './TableBody.svelte';
export { default as TableCell } from './TableCell.svelte';
export { default as TableHead } from './TableHead.svelte';
export { default as TableHeadCell } from './TableHeadCell.svelte';
export { default as TableRow } from './TableRow.svelte';
