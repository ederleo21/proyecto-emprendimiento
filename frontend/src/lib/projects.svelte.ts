// Estado de la pantalla de Proyectos de Emprendimiento.
//
// Sigue el patrón de los MFE de InnoTech: una clase con `$state`, los datos
// crudos del backend y los derivados en `$derived`.
import { api, ApiError } from '$lib/api';

export interface Stage {
  id: string;
  code: string;
  name: string;
  order: number;
  /** blue | darkblue | orange | red | green — viene del catálogo, no del front. */
  color: string;
}

export interface StageMetric {
  code: string;
  name: string;
  color: string;
  order: number;
  count: number;
}

export interface Project {
  id: string;
  code: string;
  title: string;
  stage: string | null;
  stage_code: string | null;
  stage_name: string | null;
  stage_color: string | null;
  progress: number;
  is_active: boolean;
}

const BASE = '/api/v1/entrepreneurship';

// El icono de cada tarjeta sale del color que trae el catálogo y no del código
// de la etapa: así una etapa nueva llega con icono puesto.
const ICON_BY_COLOR: Record<string, string> = {
  blue: 'files/lightbulb',
  darkblue: 'files/document',
  orange: 'files/rocket',
  red: 'interface/settings',
  green: 'files/flag',
};

// Y con qué familia de tokens se pinta. `StatCards` compone
// `var(--ds-<color>-500)`, así que acá tiene que salir un nombre de familia.
const TOKEN_BY_COLOR: Record<string, string> = {
  blue: 'info',
  darkblue: 'brand',
  orange: 'warning',
  red: 'error',
  green: 'success',
};

class ProjectsState {
  stages = $state<Stage[]>([]);
  metrics = $state<StageMetric[]>([]);
  projects = $state<Project[]>([]);
  total = $state(0);

  loading = $state(false);
  saving = $state(false);
  errorMessage = $state('');

  // Filtros de la barra de herramientas.
  stageFilter = $state('');
  search = $state('');
  // `table | card` y no `list | grid`: es el contrato del `ViewToggle` de
  // InnoTech, que este proyecto usa tal cual.
  view = $state<'table' | 'card'>('table');

  // Paginación. El backend manda cuántas páginas hay; acá solo se recuerda en
  // cuál estamos.
  page = $state(1);
  pageSize = $state(10);
  totalPages = $state(1);

  stageOptions = $derived([
    { value: '', label: 'Todos' },
    ...this.stages.map((s) => ({ value: s.code, label: s.name })),
  ]);

  /** Las tarjetas de métricas, en el formato que espera `StatCards`.
   *
   * El catálogo guarda el color como `blue`, `darkblue`… y el componente pide
   * una familia de tokens (`info`, `brand`…). La traducción vive acá y no en
   * el backend: allá el color describe la etapa, acá se decide con qué token
   * se pinta.
   */
  statItems = $derived(
    this.metrics.map((m) => ({
      label: m.name,
      value: m.count,
      icon: ICON_BY_COLOR[m.color] ?? 'files/document',
      color: TOKEN_BY_COLOR[m.color] ?? 'brand',
    })),
  );

  async loadAll() {
    this.loading = true;
    this.errorMessage = '';
    try {
      const [stages, metrics] = await Promise.all([
        api.get<Stage[]>(`${BASE}/stages/`),
        api.get<StageMetric[]>(`${BASE}/metrics/`),
      ]);
      this.stages = stages ?? [];
      this.metrics = metrics ?? [];
      await this.loadProjects();
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
    } finally {
      this.loading = false;
    }
  }

  /** Relee solo el listado. Lo llaman los filtros, que no cambian métricas. */
  async loadProjects() {
    const params = new URLSearchParams();
    if (this.stageFilter) params.set('stage', this.stageFilter);
    if (this.search.trim()) params.set('search', this.search.trim());
    params.set('page', String(this.page));
    params.set('page_size', String(this.pageSize));

    try {
      const data = await api.get<{
        results: Project[];
        count: number;
        page: number;
        page_size: number;
        total_pages: number;
      }>(`${BASE}/projects/?${params.toString()}`);

      this.projects = data?.results ?? [];
      this.total = data?.count ?? 0;
      this.totalPages = data?.total_pages ?? 1;
      // La página la confirma el backend: si se pidió una que no existe,
      // `get_page` devuelve la más cercana y hay que reflejarlo.
      this.page = data?.page ?? 1;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
    }
  }

  /** Cambia de página. */
  async goToPage(page: number) {
    this.page = page;
    await this.loadProjects();
  }

  /** Relee desde la primera página. Lo llaman los filtros: con el filtro nuevo
   *  la página 5 puede ya no existir. */
  async applyFilters() {
    this.page = 1;
    await this.loadProjects();
  }

  /** Devuelve el proyecto creado, o `null` si falló. */
  async createProject(title: string): Promise<Project | null> {
    this.saving = true;
    this.errorMessage = '';
    try {
      const created = await api.post<Project>(`${BASE}/projects/`, { title });
      // Se recarga todo: al crear cambian las métricas, no solo la tabla.
      await this.loadAll();
      return created;
    } catch (e) {
      this.errorMessage = e instanceof ApiError ? e.firstMessage : String(e);
      return null;
    } finally {
      this.saving = false;
    }
  }
}

export const projectsState = new ProjectsState();
