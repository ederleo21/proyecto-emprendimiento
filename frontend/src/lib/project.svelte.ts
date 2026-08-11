// Estado del tablero de un proyecto: sus etapas, sus actividades y el avance.
//
// El avance NO se guarda: lo calcula el backend contando actividades
// confirmadas sobre aplicables. Acá solo se muestra.
import { api, ApiError } from '$lib/api';

export interface Activity {
  id: string;
  code: string;
  name: string;
  order: number;
  /** Elegible por proyecto. Las fijas aplican siempre. */
  is_optional: boolean;
  /** No se confirma a mano: se marca sola. El botón sale deshabilitado. */
  is_derived: boolean;
  /** Si cuenta para el avance de este proyecto. */
  applies: boolean;
  is_confirmed: boolean;
  confirmed_at: string | null;
}

export interface ProjectStage {
  id: string;
  code: string;
  name: string;
  order: number;
  color: string;
  progress: number;
  activities: Activity[];
}

export interface ProjectHead {
  id: string;
  code: string;
  title: string;
  stage_name: string | null;
  progress: number;
}

const BASE = '/api/v1/entrepreneurship';

class ProjectState {
  project = $state<ProjectHead | null>(null);
  stages = $state<ProjectStage[]>([]);

  loading = $state(false);
  errorMessage = $state('');
  /** Etapa abierta en el panel de actividades. `null` = solo el tablero. */
  openStage = $state<string | null>(null);

  stage(code: string) {
    return this.stages.find((s) => s.code === code) ?? null;
  }

  async load(id: string) {
    this.loading = true;
    this.errorMessage = '';
    try {
      const data = await api.get<{ project: ProjectHead; stages: ProjectStage[] }>(
        `${BASE}/projects/${id}/`,
      );
      this.project = data?.project ?? null;
      this.stages = data?.stages ?? [];
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
    } finally {
      this.loading = false;
    }
  }

  /** Marca o desmarca una actividad como hecha. */
  async toggleConfirmed(activity: Activity) {
    if (!this.project) return;
    await this.send(activity, { is_confirmed: !activity.is_confirmed });
  }

  /** Agrega o quita del proyecto una actividad elegible. */
  async toggleApplies(activity: Activity) {
    if (!this.project || !activity.is_optional) return;
    await this.send(activity, { applies: !activity.applies });
  }

  private async send(activity: Activity, body: Record<string, unknown>) {
    const id = this.project!.id;
    try {
      await api.post(`${BASE}/projects/${id}/activities/${activity.id}/`, body);
      // Se recarga el detalle completo: cambiar una actividad mueve el avance
      // de su etapa y el global, y recalcular acá duplicaría la regla que ya
      // vive en el backend.
      await this.load(id);
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
    }
  }
}

export const projectState = new ProjectState();
