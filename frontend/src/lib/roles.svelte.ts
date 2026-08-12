// Roles y permisos.
//
// Los permisos se declaran en el código del backend y llegan como catálogo de
// solo lectura: existen porque hay código que los comprueba. Lo que se
// gestiona son los roles, que son combinaciones de ellos.
import { api, ApiError } from '$lib/api';

export interface Role {
  id: string;
  code: string;
  name: string;
  description: string;
  scope: 'INSTITUTIONAL' | 'PROJECT';
  scope_label: string;
  is_system: boolean;
  is_active: boolean;
  /** Cuántas personas lo tienen asignado. */
  people: number;
  permission_count: number;
  /** Solo en el detalle. */
  permissions?: string[];
}

export interface PermissionItem {
  code: string;
  description: string;
}

export interface PermissionModule {
  module: string;
  permissions: PermissionItem[];
}

const BASE = '/api/v1/roles';

class RolesState {
  roles = $state<Role[]>([]);
  catalog = $state<PermissionModule[]>([]);
  current = $state<Role | null>(null);

  loading = $state(false);
  saving = $state(false);
  errorMessage = $state('');

  /** Los de cargo y los de proyecto, separados: son cosas distintas y
   *  mezclarlos en una sola lista confunde a quien reparte permisos. */
  institutional = $derived(this.roles.filter((r) => r.scope === 'INSTITUTIONAL'));
  perProject = $derived(this.roles.filter((r) => r.scope === 'PROJECT'));

  async loadAll() {
    this.loading = true;
    this.errorMessage = '';
    try {
      const [roles, catalog] = await Promise.all([
        api.get<Role[]>(`${BASE}/`),
        api.get<PermissionModule[]>(`${BASE}/permissions/`),
      ]);
      this.roles = roles ?? [];
      this.catalog = catalog ?? [];
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
    } finally {
      this.loading = false;
    }
  }

  async load(id: string) {
    this.loading = true;
    this.errorMessage = '';
    try {
      const [role, catalog] = await Promise.all([
        api.get<Role>(`${BASE}/${id}/`),
        api.get<PermissionModule[]>(`${BASE}/permissions/`),
      ]);
      this.current = role ?? null;
      this.catalog = catalog ?? [];
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
    } finally {
      this.loading = false;
    }
  }

  async create(name: string, description: string, cloneFrom: string): Promise<Role | null> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const created = await api.post<Role>(`${BASE}/`, {
        name,
        description,
        clone_from: cloneFrom || null,
      });
      await this.loadAll();
      return created;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      return null;
    } finally {
      this.saving = false;
    }
  }

  /** Guarda los permisos de un rol. El backend rechaza dejar a la institución
   *  sin nadie que pueda repartirlos. */
  async savePermissions(id: string, permissions: string[]): Promise<boolean> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const updated = await api.patch<Role>(`${BASE}/${id}/`, { permissions });
      if (updated) this.current = updated;
      return true;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      return false;
    } finally {
      this.saving = false;
    }
  }

  async remove(id: string): Promise<boolean> {
    this.saving = true;
    this.errorMessage = '';
    try {
      await api.delete(`${BASE}/${id}/`);
      await this.loadAll();
      return true;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      return false;
    } finally {
      this.saving = false;
    }
  }
}

export const rolesState = new RolesState();
