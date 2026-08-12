// Identidad visual de la institución activa.
//
// El color de marca lo configura cada institución, no está escrito en el
// código. Se pide al backend y se inyecta sobre los tokens del design system
// sobreescribiendo `--ds-brand-*`. Mismo criterio que el branding del
// monorepo de InnoTech.
//
// Además se recuerda lo último que se supo. Sin eso, cada recarga muestra un
// instante los colores por defecto del CSS y salta a los de la institución
// cuando llega la respuesta del servidor. Con la copia guardada se pinta lo
// conocido de entrada y la respuesta solo confirma o corrige.
import { browser } from '$app/environment';

import { api, ApiError } from '$lib/api';

const CACHE_KEY = 'outreach.branding';

// Las variables de color ya resueltas. Las lee el script de `app.html` antes
// de que la página se pinte — si cambia este nombre, hay que cambiarlo allá.
const VARS_KEY = 'outreach.branding.vars';

export interface Branding {
  name: string;
  subtitle: string;
  primary_color: string;
  secondary_color: string;
  /** Absoluta: el navegador la pide a otro origen que el de esta aplicación. */
  logo_url: string | null;
  tenant: string | null;
}

// Los mismos neutros que trae el branding de InnoTech por defecto.
const FALLBACK: Branding = {
  name: 'Vinculación con la Sociedad',
  subtitle: '',
  primary_color: '#349AFE',
  secondary_color: '#150089',
  logo_url: null,
  tenant: null,
};

/** Lo último que se supo, o null. Nunca lanza: un dato guardado que no se
 *  entiende se ignora y se sigue con los valores por defecto. */
function readCache(): Branding | null {
  if (!browser) return null;
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    // Se comprueba lo mínimo: si el formato cambió entre versiones, mejor
    // descartarlo que pintar la pantalla con algo a medias.
    return parsed?.primary_color && parsed?.secondary_color ? parsed : null;
  } catch {
    return null;
  }
}

function writeCache(branding: Branding) {
  if (!browser) return;
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(branding));
  } catch {
    // Sin espacio o en modo privado: no es motivo para romper nada.
  }
}

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
/** Los cinco pasos de una familia, como pares listos para aplicar. */
function ramp(family: string, color: string): Record<string, string> {
  return {
    [`--ds-${family}-500`]: color,
    [`--ds-${family}-600`]: shade(color, -0.2),
    [`--ds-${family}-700`]: shade(color, -0.45),
    [`--ds-${family}-300`]: shade(color, 0.6),
    [`--ds-${family}-100`]: shade(color, 0.9),
  };
}

/**
 * Las variables que le corresponden a una identidad.
 *
 * El primario va sobre `--ds-brand-*`, que es lo que pinta botones, enlaces y
 * estados activos. El secundario va sobre `--ds-info-*`, que es la familia que
 * el design system usa para acentos — así un solo color de apoyo se refleja
 * sin tener que tocar componente por componente.
 */
function brandingVars(branding: Branding): Record<string, string> {
  return {
    ...ramp('brand', branding.primary_color),
    ...ramp('info', branding.secondary_color),
  };
}

/** Aplica la identidad de la institución sobre los tokens. */
export function applyBranding(branding: Branding) {
  if (!browser) return;
  const root = document.documentElement;
  const vars = brandingVars(branding);
  for (const [name, value] of Object.entries(vars)) {
    root.style.setProperty(name, value);
  }
  // Se dejan resueltas para el script de `app.html`, que corre antes de que la
  // página se pinte y no puede calcularlas.
  try {
    localStorage.setItem(VARS_KEY, JSON.stringify(vars));
  } catch {
    // Sin espacio o en modo privado: solo significa que la próxima recarga
    // volverá a parpadear.
  }
}

class BrandingState {
  // Se arranca con lo último que se supo, no con el neutro: es lo que evita
  // el salto de color al recargar.
  data = $state<Branding>(readCache() ?? FALLBACK);
  loading = $state(true);
  saving = $state(false);
  errorMessage = $state('');

  /** Deja la identidad como la fuente de verdad, la pinta y la recuerda. */
  private adopt(branding: Branding) {
    this.data = branding;
    applyBranding(branding);
    writeCache(branding);
  }

  async load() {
    try {
      const branding = await api.get<Branding>('/api/v1/branding/');
      if (branding) this.adopt(branding);
    } catch {
      // Sin branding la aplicación tiene que funcionar igual: se queda con lo
      // que había, sea la copia guardada o los valores por defecto.
      console.warn('[branding] no se pudo cargar; se usa lo último conocido');
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
  async save(changes: Partial<Branding>): Promise<boolean> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const updated = await api.patch<Branding>('/api/v1/branding/settings/', changes);
      if (updated) this.adopt(updated);
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

  /** Sube el logotipo. Se guarda al instante, sin pasar por "Guardar": un
   *  archivo no se edita como un campo de texto, o está o no está. */
  async uploadLogo(file: File): Promise<boolean> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const updated = await api.upload<Branding>(
        '/api/v1/branding/settings/logo/', 'logo', file,
      );
      if (updated) this.adopt(updated);
      return true;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      return false;
    } finally {
      this.saving = false;
    }
  }

  async removeLogo(): Promise<boolean> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const updated = await api.delete<Branding>('/api/v1/branding/settings/logo/');
      if (updated) this.adopt(updated);
      return true;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      return false;
    } finally {
      this.saving = false;
    }
  }
}

export const branding = new BrandingState();

// Se pinta al cargar el módulo, no en `onMount`: para cuando un componente se
// monta, el navegador ya dibujó una vez. Acá todavía no, así que los colores
// de la institución entran antes del primer trazo y no se ve el salto.
//
// Solo aplica si había algo recordado; si no, quedan los del CSS hasta que
// responda el servidor.
if (browser) applyBranding(branding.data);
