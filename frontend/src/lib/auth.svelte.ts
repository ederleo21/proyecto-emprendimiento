// Sesión del usuario en el modo suelto.
//
// El token lo emite ESTE servicio (`/api/v1/auth/sign-in/`), no el IAM de
// InnoTech: el proyecto tiene que funcionar sin depender de aquel stack.
// Pero los claims son los mismos, así que integrarlo es cambiar de dónde sale
// el token, no cómo se usa.
//
// De dónde sale ese token en cada modo lo decide `lib/session.ts`. Acá solo
// vive el acceso propio, que es el respaldo cuando no hay shell.
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { base } from '$app/paths';
import { OWN_ACCESS, OWN_REFRESH, OWN_USER, clearSession, currentToken } from '$lib/session';

const ACCESS_KEY = OWN_ACCESS;
const REFRESH_KEY = OWN_REFRESH;

export interface SessionUser {
  id: string;
  username: string;
  email: string;
  full_name: string;
  is_superuser: boolean;
}

class AuthState {
  access = $state<string | null>(null);
  user = $state<SessionUser | null>(null);
  loading = $state(false);
  errorMessage = $state('');

  isAuthenticated = $derived(!!this.access);

  /** Recupera la sesión guardada. Se llama al arrancar la aplicación.
   *
   * Pasa por `currentToken()` y no por la clave propia: embebida, la sesión
   * viene del shell y hay que consumirla del fragmento de la URL.
   */
  restore() {
    if (!browser) return;
    this.access = currentToken();
    const raw = localStorage.getItem(OWN_USER);
    if (raw) {
      try {
        this.user = JSON.parse(raw);
      } catch {
        this.user = null;
      }
    }
  }

  async signIn(username: string, password: string): Promise<boolean> {
    this.loading = true;
    this.errorMessage = '';
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL ?? 'http://localhost:8100'}/api/v1/auth/sign-in/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        },
      );
      const body = await res.json().catch(() => null);

      if (!res.ok) {
        this.errorMessage = body?.message ?? `Error HTTP ${res.status}`;
        return false;
      }

      const { access, refresh, user } = body.data;
      this.access = access;
      this.user = user;
      if (browser) {
        localStorage.setItem(ACCESS_KEY, access);
        localStorage.setItem(REFRESH_KEY, refresh);
        localStorage.setItem(OWN_USER, JSON.stringify(user));
      }
      return true;
    } catch (e) {
      this.errorMessage = 'No se pudo contactar al servidor.';
      return false;
    } finally {
      this.loading = false;
    }
  }

  signOut() {
    this.access = null;
    this.user = null;
    clearSession();
    goto(`${base}/login`);
  }
}

export const auth = new AuthState();
