// De dónde sale el token, en los dos modos en que corre esta aplicación.
//
// **Embebida** en el shell de InnoTech: la sesión llega en el fragmento de la
// URL del iframe, que es como el shell se la pasa a todos los micro-frontends
// (`withAuthFragment` del lado del shell, `getTokenFromHash` del lado del MFE):
//
//     .../mfe/outreach/#token=eyJ…&refresh_token=eyJ…
//
// Se guarda bajo las claves del ecosistema — `token` y `refresh_token` — que
// son las que usan los demás MFE. No es capricho: en desarrollo cada uno vive
// en un puerto distinto y `localStorage` está aislado por puerto, así que el
// fragmento es la única vía por la que la sesión cruza.
//
// **Suelta**, sin shell: la escribe la pantalla de acceso propia bajo sus
// claves `outreach.*`. Es lo que permite trabajar sin levantar InnoTech.
//
// El orden importa: si hay sesión del shell, esa manda.
import { browser } from '$app/environment';

// Claves del ecosistema, compartidas con el resto de micro-frontends.
const SHELL_ACCESS = 'token';
const SHELL_REFRESH = 'refresh_token';

// Claves propias del modo suelto.
export const OWN_ACCESS = 'outreach.access';
export const OWN_REFRESH = 'outreach.refresh';
export const OWN_USER = 'outreach.user';

/** Si corremos dentro del iframe del shell. */
export function isEmbedded(): boolean {
  if (!browser) return false;
  try {
    return window.self !== window.top;
  } catch {
    // Un shell de otro origin hace que el acceso lance, y eso solo pasa
    // estando dentro de un iframe.
    return true;
  }
}

/** Toma el token del fragmento, lo guarda y lo borra de la URL.
 *
 * Limpiar la URL no es cosmético: si el fragmento queda, el token entra al
 * historial del navegador y viaja en cualquier enlace que alguien copie.
 */
function takeTokenFromHash(): string | null {
  if (!browser) return null;

  const raw = location.hash.startsWith('#') ? location.hash.slice(1) : location.hash;
  if (!raw) return null;

  const params = new URLSearchParams(raw);
  const access = params.get('token');
  if (!access) return null;

  localStorage.setItem(SHELL_ACCESS, access);
  const refresh = params.get('refresh_token');
  if (refresh) localStorage.setItem(SHELL_REFRESH, refresh);

  params.delete('token');
  params.delete('refresh_token');
  const rest = params.toString();
  history.replaceState(
    null,
    document.title,
    `${location.pathname}${location.search}${rest ? `#${rest}` : ''}`,
  );

  return access;
}

/** El token vigente, mire donde mire. */
export function currentToken(): string | null {
  if (!browser) return null;
  return (
    takeTokenFromHash() ??
    localStorage.getItem(SHELL_ACCESS) ??
    localStorage.getItem(OWN_ACCESS)
  );
}

/** Borra la sesión de los dos modos. */
export function clearSession(): void {
  if (!browser) return;
  for (const key of [SHELL_ACCESS, SHELL_REFRESH, OWN_ACCESS, OWN_REFRESH, OWN_USER]) {
    localStorage.removeItem(key);
  }
}
