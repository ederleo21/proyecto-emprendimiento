<!-- Copia de `@innotech/ui-svelte/components/ConfirmModal.svelte` del monorepo de
     InnoTech. Sin cambios. -->
<script lang="ts">
  /**
   * Modal de confirmación de acción (success / confirm / delete).
   *
   * Diseñado para reusarse en cualquier flujo CRUD donde haya que confirmar
   * una operación. Soporta listar dependencias activas (catálogos en cascada)
   * y un tercer botón opcional ("Desactivar en cascada", "Forzar borrado", …).
   */
  import Modal from './Modal.svelte';
  import Button from './Button.svelte';
  import Icon from './Icon.svelte';

  export interface DependencyItem {
    label: string;
    count: number;
    examples: string[];
  }

  interface Props {
    open: boolean;
    variant?: 'success' | 'confirm' | 'delete';
    title: string;
    message?: string;
    dependencies?: DependencyItem[];
    total?: number;
    primaryLabel?: string;
    cancelLabel?: string;
    cascadeLabel?: string;
    loading?: boolean;
    /** Cuando hay dependencies > 0 se oculta el botón primary. Útil para no
     *  permitir borrado simple cuando bloquear es obligatorio. Default: true. */
    hidePrimaryWhenBlocked?: boolean;
    onConfirm: () => void;
    onCascade?: () => void;
    onCancel: () => void;
  }

  let {
    open,
    variant = 'confirm',
    title,
    message,
    dependencies = [],
    total = 0,
    primaryLabel,
    cancelLabel = 'Cancelar',
    cascadeLabel,
    loading = false,
    hidePrimaryWhenBlocked = true,
    onConfirm,
    onCascade,
    onCancel,
  }: Props = $props();

  const defaultPrimaryLabel = $derived(
    primaryLabel
      ?? (variant === 'success' ? 'Aceptar'
        : variant === 'delete'  ? 'Eliminar'
        :                          'Guardar'),
  );

  // Icono + colores semánticos por variante (todo desde tokens DS 2.0).
  const variantIcon = $derived(
    variant === 'success' ? 'interface/check'
      : variant === 'delete' ? 'interface/trash'
      :                        'interface/save',
  );
  const variantClass = $derived(`confirm-modal--${variant}`);

  const hasDeps = $derived(dependencies.length > 0 && total > 0);
  const showPrimary = $derived(!(hasDeps && hidePrimaryWhenBlocked));
  const showCascade = $derived(hasDeps && !!cascadeLabel && !!onCascade);

  function handleCancel() {
    if (loading) return;
    onCancel();
  }

  function handleConfirm() {
    if (loading) return;
    onConfirm();
  }

  function handleCascade() {
    if (loading || !onCascade) return;
    onCascade();
  }
</script>

<Modal
  {open}
  size="sm"
  showClose={false}
  closeOnOutsideClick={false}
  onclose={handleCancel}
>
  {#snippet header()}
    <div class="confirm-modal__header {variantClass}">
      <div class="confirm-modal__icon-wrap" aria-hidden="true">
        <Icon name={variantIcon} size="md" />
      </div>
      <div class="confirm-modal__title-group">
        <h6 class="confirm-modal__title">{title}</h6>
      </div>
      <button
        type="button"
        class="confirm-modal__close"
        onclick={handleCancel}
        aria-label="Cerrar"
        disabled={loading}
      >
        <Icon name="design-system/close" size="md" />
      </button>
    </div>
  {/snippet}

  {#snippet body()}
    <div class="confirm-modal__body">
      {#if message}
        <p class="confirm-modal__message">{message}</p>
      {/if}

      {#if hasDeps}
        <div class="confirm-modal__deps">
          <p class="confirm-modal__deps-intro">
            Este registro tiene <strong>{total}</strong> dependencia(s) activa(s):
          </p>
          <ul class="confirm-modal__deps-list">
            {#each dependencies as dep (dep.label)}
              <li class="confirm-modal__deps-item">
                <span class="confirm-modal__deps-count">{dep.count}</span>
                <span class="confirm-modal__deps-label">{dep.label}</span>
                {#if dep.examples?.length}
                  <span class="confirm-modal__deps-examples">
                    ({dep.examples.slice(0, 3).join(', ')}{dep.examples.length > 3 ? '…' : ''})
                  </span>
                {/if}
              </li>
            {/each}
          </ul>
          {#if showCascade}
            <p class="confirm-modal__deps-note">
              Desactivarlo en cascada también desactivará todos los dependientes
              listados arriba.
            </p>
          {/if}
        </div>
      {/if}
    </div>
  {/snippet}

  {#snippet footer()}
    <div class="confirm-modal__footer">
      <Button
        variant="ghost"
        size="md"
        onclick={handleCancel}
        disabled={loading}
      >
        {cancelLabel}
      </Button>
      {#if showCascade}
        <Button
          variant="danger"
          size="md"
          onclick={handleCascade}
          disabled={loading}
          loading={loading}
        >
          {cascadeLabel}
        </Button>
      {/if}
      {#if showPrimary}
        <Button
          variant={variant === 'delete' ? 'danger' : 'primary'}
          size="md"
          onclick={handleConfirm}
          disabled={loading}
          loading={loading}
        >
          {defaultPrimaryLabel}
        </Button>
      {/if}
    </div>
  {/snippet}
</Modal>

<style>
  .confirm-modal__header {
    display: flex;
    align-items: center;
    gap: var(--ds-space-3, 12px);
    width: 100%;
    padding-right: 8px;
  }

  .confirm-modal__icon-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .confirm-modal--success .confirm-modal__icon-wrap {
    background: var(--ds-success-100);
    color: var(--ds-success-700);
  }
  .confirm-modal--confirm .confirm-modal__icon-wrap {
    background: var(--ds-info-100);
    color: var(--ds-info-700);
  }
  .confirm-modal--delete .confirm-modal__icon-wrap {
    background: var(--ds-error-100);
    color: var(--ds-error-700);
  }

  .confirm-modal__title-group {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .confirm-modal__title {
    margin: 0;
    font-size: 18px;
    font-weight: 800;
    color: var(--ds-neutral-700);
    line-height: 1.2;
  }

  .confirm-modal__close {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    color: var(--ds-neutral-500);
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.18s ease;
    flex-shrink: 0;
  }
  .confirm-modal__close:hover:not(:disabled) {
    background: var(--ds-neutral-100);
    color: var(--ds-neutral-700);
    transform: rotate(90deg);
  }
  .confirm-modal__close:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .confirm-modal__body {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .confirm-modal__message {
    margin: 0;
    font-size: var(--ds-body-m, 14px);
    line-height: 1.5;
    color: var(--ds-neutral-600);
  }

  .confirm-modal__deps {
    background: var(--ds-warning-100);
    border: 1px solid var(--ds-warning-300);
    border-radius: var(--ds-radius-md, 12px);
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .confirm-modal__deps-intro {
    margin: 0;
    font-size: var(--ds-body-m, 14px);
    color: var(--ds-warning-700);
    font-weight: 600;
  }
  .confirm-modal__deps-intro strong {
    font-weight: 800;
  }

  .confirm-modal__deps-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .confirm-modal__deps-item {
    display: flex;
    align-items: baseline;
    gap: 8px;
    flex-wrap: wrap;
    font-size: var(--ds-body-s, 12px);
    color: var(--ds-neutral-700);
    line-height: 1.4;
  }
  .confirm-modal__deps-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 28px;
    padding: 0 8px;
    height: 22px;
    border-radius: 999px;
    background: var(--ds-warning-600);
    color: white;
    font-weight: 800;
    font-size: 12px;
    flex-shrink: 0;
  }
  .confirm-modal__deps-label {
    font-weight: 700;
  }
  .confirm-modal__deps-examples {
    color: var(--ds-neutral-600);
    font-style: italic;
  }
  .confirm-modal__deps-note {
    margin: 0;
    font-size: var(--ds-body-s, 12px);
    color: var(--ds-warning-700);
    font-weight: 500;
  }

  .confirm-modal__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    width: 100%;
    flex-wrap: wrap;
  }
</style>
