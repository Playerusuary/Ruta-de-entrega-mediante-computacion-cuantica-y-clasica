/**
 * Formas de los datos que devuelve el backend.
 *
 * Es el espejo en TypeScript de `backend/app/esquemas.py`. Si cambia el
 * contrato alla, cambia aqui: es la unica fuente de verdad del frontend sobre
 * como viene el JSON.
 */

/** Un destino sobre un nodo de la cuadricula. El id 0 es siempre el deposito. */
export interface Punto {
  id: number;
  /** Columna del nodo en la cuadricula (0..grid_size). NO son pixeles. */
  x: number;
  /** Fila del nodo en la cuadricula (0..grid_size). NO son pixeles. */
  y: number;
  etiqueta: string;
}

/** Una ruta del catalogo que comparten ambos modos. */
export interface Ruta {
  id: number;
  /** Ids de los puntos en orden de recorrido. Si es cerrada, vuelve al deposito. */
  orden: number[];
  distancia: number;
}

export type OrdenEvaluacion = "secuencial" | "aleatorio";

/** Un frame del modo clasico: una ruta evaluada. */
export interface PasoClasico {
  /** Contador de rutas evaluadas, arranca en 1. */
  indice: number;
  ruta_id: number;
  ruta: number[];
  distancia: number;
  /** True si esta ruta rompio el record: merece enfasis visual. */
  es_mejor: boolean;
  mejor_ruta: number[];
  mejor_distancia: number;
}

export interface SimulacionClasica {
  modo: "clasico";
  rutas: Ruta[];
  total_rutas: number;
  pasos: PasoClasico[];
  mejor_ruta_id: number;
  mejor_ruta: number[];
  mejor_distancia: number;
  rutas_evaluadas: number;
  /** Ids que empatan en la distancia minima. Con Manhattan son la norma. */
  empates_en_la_mejor: number[];
}

export interface ProbabilidadRuta {
  ruta_id: number;
  distancia: number;
  probabilidad: number;
}

/** Un frame del modo cuantico: una iteracion de amplificacion. */
export interface PasoCuantico {
  /** 0 = superposicion inicial; luego 1, 2, 3... */
  indice: number;
  /** Probabilidad de TODAS las rutas. Ninguna desaparece: eso es superposicion. */
  probabilidades: ProbabilidadRuta[];
  visibles: number[];
  eliminadas_en_esta_ronda: number[];
  /** Probabilidad acumulada de las rutas marcadas: la "confianza" del sistema. */
  probabilidad_marcadas: number;
}

export interface SimulacionCuantica {
  modo: "cuantico";
  rutas: Ruta[];
  total_rutas: number;
  pasos: PasoCuantico[];
  /** Consultas al oraculo. Es el numero a comparar contra rutas_evaluadas. */
  iteraciones: number;
  rutas_marcadas: number[];
  medicion_id: number;
  medicion_ruta: number[];
  medicion_distancia: number;
  /** Si la medicion cayo en una ruta marcada. Puede fallar: es probabilistico. */
  acerto: boolean;
  probabilidad_final_marcadas: number;
}

/** Respuesta de GET /api/v1/escenario: el mapa y los dos modos ya resueltos. */
export interface Escenario {
  grid_size: number;
  puntos: Punto[];
  rutas: Ruta[];
  cerrada: boolean;
  semilla: number | null;
  clasico: SimulacionClasica;
  cuantico: SimulacionCuantica;
  rutas_evaluadas_clasico: number;
  iteraciones_cuantico: number;
}

/** Opciones con las que se pide un escenario. */
export interface OpcionesEscenario {
  n: number;
  cerrada: boolean;
  orden?: OrdenEvaluacion;
  semilla?: number | null;
  grid_size?: number;
}

export type ModoSimulacion = "clasico" | "cuantico";

export type EstadoSimulacion =
  /** Hay mapa cargado pero no se ha corrido ningun modo. */
  | "inactivo"
  /** Pidiendo un escenario nuevo al backend. */
  | "cargando"
  /** Animando la traza. */
  | "corriendo"
  /** Termino: se muestra la ruta ganadora. */
  | "finalizado";
