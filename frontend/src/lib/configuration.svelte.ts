// Parámetros del módulo de emprendimiento para esta institución.
//
// Lo que acá se guarda decide cómo se comporta el módulo — hoy el formato del
// código de proyecto, mañana los plazos y las reglas de etapa. Es el lugar al
// que van las decisiones del proceso, en vez de quedar escritas en el código.
import { api, ApiError } from '$lib/api';

export interface Configuration {
  id: string;
  project_code_prefix: string;
  project_code_include_year: boolean;
  project_code_digits: number;
  /** Cómo quedaría el próximo código. Lo calcula el backend: la regla vive
   *  allá y rearmarla acá sería tenerla en dos sitios. */
  code_example: string;
}

const BASE = '/api/v1/entrepreneurship';

class ConfigurationState {
  data = $state<Configuration | null>(null);
  loading = $state(false);
  saving = $state(false);
  errorMessage = $state('');

  async load() {
    this.loading = true;
    this.errorMessage = '';
    try {
      this.data = await api.get<Configuration>(`${BASE}/configuration/`);
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
    } finally {
      this.loading = false;
    }
  }

  /** Guarda los cambios. Requiere administrador — lo valida el backend. */
  async save(changes: Partial<Configuration>): Promise<boolean> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const updated = await api.patch<Configuration>(`${BASE}/configuration/`, changes);
      if (updated) this.data = updated;
      return true;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      return false;
    } finally {
      this.saving = false;
    }
  }
}

export const configuration = new ConfigurationState();
