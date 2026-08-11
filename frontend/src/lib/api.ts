// Cliente HTTP del servicio Outreach.
//
// El backend responde siempre con el envoltorio {status, message, data, errors},
// igual que los servicios de InnoTech. `request` saca el `data` para que las
// pantallas no tengan que conocer esa forma.
import { browser } from '$app/environment';
import { base } from '$app/paths';
import { clearSession, currentToken, isEmbedded } from '$lib/session';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8100';
const TENANT = import.meta.env.VITE_TENANT_SCHEMA ?? '';

export interface Envelope<T> {
  status: 'success' | 'error';
  message: string;
  data: T | null;
  errors: Record<string, string[]> | null;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly errors: Record<string, string[]> | null = null,
  ) {
    super(message);
  }

  /** Primer mensaje legible, para mostrar en pantalla. */
  get firstMessage(): string {
    if (this.errors) {
      const first = Object.values(this.errors)[0];
      if (Array.isArray(first) && first.length) return String(first[0]);
    }
    return this.message;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Content-Type', 'application/json');

  // Se lee en cada petición para no depender del orden de carga de los módulos
  // (el store de sesión importa este archivo).
  const token = currentToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);

  // El backend resuelve la institución por Host; desde el navegador el Host es
  // `localhost`, así que se manda explícita. Ver `RobustTenantMiddleware`.
  if (TENANT) headers.set('X-Tenant-Schema', TENANT);

  const response = await fetch(`${BASE}${path}`, { ...init, headers });

  let body: Envelope<T> | null = null;
  try {
    body = await response.json();
  } catch {
    // Respuestas sin cuerpo (204) o errores del gateway en HTML.
  }

  if (!response.ok) {
    // Sesión vencida o inválida: se limpia y se manda al acceso. Sin esto la
    // pantalla se queda mostrando errores sin explicar qué hacer.
    //
    // Embebida no se redirige: la sesión es del shell, y mandar el iframe a
    // nuestro /login mostraría una pantalla de acceso dentro de otra. Allá el
    // shell se encarga de renovar o de echar al usuario.
    if (response.status === 401 && browser) {
      clearSession();
      if (!isEmbedded() && !location.pathname.startsWith(`${base}/login`)) {
        location.href = `${base}/login`;
      }
    }
    throw new ApiError(
      body?.message ?? `Error HTTP ${response.status}`,
      response.status,
      body?.errors ?? null,
    );
  }
  return (body?.data ?? null) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
