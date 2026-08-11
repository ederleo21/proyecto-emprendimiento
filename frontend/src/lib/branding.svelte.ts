// Identidad visual de la institución activa.
//
// El color de marca lo configura cada institución, no está escrito en el
// código. Se pide al backend y se inyecta sobre los tokens del design system
// sobreescribiendo `--ds-brand-*`. Mismo criterio que el branding del
// monorepo de InnoTech.
import { api, ApiError } from '$lib/api';

export interface Branding {
  name: string;
  primary_color: string;
  secondary_color: string;
  tenant: string | null;
}

// Los mismos neutros que trae el branding de InnoTech por defecto.
const FALLBACK: Branding = {
  name: 'Vinculación con la Sociedad',
  primary_color: '#349AFE',
  secondary_color: '#150089',
  tenant: null,
};

/** #RGB o #RRGGBB → [r, g, b]. Devuelve null si el color no es válido. */
function hexToRgb(hex: string): [number, number, number] | null {
  const clean = hex.trim().replace('#', '');
  const full = clean.length === 3
    ? clean.split('').map((c) => c + c).join('')
    : clean;
  if (!/^[0-9a-fA-F]{6}$/.test(full)) return null;
  return [
    parseInt(full.slice(0, 2), 16),
    parseInt(full.slice(2, 4), 16),
    parseInt(full.slice(4, 6), 16),
  ];
}

/** Mezcla hacia blanco (amount > 0) o hacia negro (amount < 0). */
function shade(hex: string, amount: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  const mixed = rgb.map((channel) => {
    const target = amount > 0 ? 255 : 0;
    const value = Math.round(channel + (target - channel) * Math.abs(amount));
    return Math.max(0, Math.min(255, value));
  });
  return '#' + mixed.map((c) => c.toString(16).padStart(2, '0')).join('').toUpperCase();
}

/**
 * Escribe una rampa de cinco pasos a partir de un solo color.
 *
 * La institución configura UN color por familia; el design system necesita
 * cinco. Los otros cuatro se derivan mezclando hacia blanco o negro, en las
 * mismas proporciones que usa la rampa de InnoTech.
 */
function applyRamp(family: string, color: string) {
  const root = document.documentElement;
  root.style.setProperty(`--ds-${family}-500`, color);
  root.style.setProperty(`--ds-${family}-600`, shade(color, -0.2));
  root.style.setProperty(`--ds-${family}-700`, shade(color, -0.45));
  root.style.setProperty(`--ds-${family}-300`, shade(color, 0.6));
  root.style.setProperty(`--ds-${family}-100`, shade(color, 0.9));
}

/**
 * Aplica la identidad de la institución sobre los tokens.
 *
 * El primario va sobre `--ds-brand-*`, que es lo que pinta botones, enlaces y
 * estados activos. El secundario va sobre `--ds-info-*`, que es la familia que
 * el design system usa para acentos — así un solo color de apoyo se refleja
 * sin tener que tocar componente por componente.
 */
export function applyBranding(branding: Branding) {
  applyRamp('brand', branding.primary_color);
  applyRamp('info', branding.secondary_color);
}

class BrandingState {
  data = $state<Branding>(FALLBACK);
  loading = $state(true);
  saving = $state(false);
  errorMessage = $state('');

  async load() {
    try {
      const branding = await api.get<Branding>('/api/v1/branding/');
      if (branding) {
        this.data = branding;
        applyBranding(branding);
      }
    } catch {
      // Sin branding la aplicación tiene que funcionar igual: se queda con el
      // color por defecto de los tokens.
      console.warn('[branding] no se pudo cargar; se usan los valores por defecto');
    } finally {
      this.loading = false;
    }
  }

  /** Pinta unos colores sin guardarlos. Lo usa la vista previa de la pantalla
   *  de personalización: se ve el cambio antes de decidir. */
  preview(primary: string, secondary: string) {
    applyBranding({ ...this.data, primary_color: primary, secondary_color: secondary });
  }

  /** Deshace la vista previa y vuelve a lo que está guardado. */
  restore() {
    applyBranding(this.data);
  }

  /** Guarda la identidad. Requiere administrador — lo valida el backend. */
  async save(primary: string, secondary: string): Promise<boolean> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const updated = await api.patch<Branding>('/api/v1/branding/settings/', {
        primary_color: primary,
        secondary_color: secondary,
      });
      if (updated) {
        this.data = updated;
        applyBranding(updated);
      }
      return true;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      // Lo que quedó pintado por la vista previa no se guardó: se revierte
      // para no mentirle al usuario sobre el estado real.
      this.restore();
      return false;
    } finally {
      this.saving = false;
    }
  }
}

export const branding = new BrandingState();
