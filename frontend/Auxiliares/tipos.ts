/**
 * ============================================================================
 * Auxiliares/tipos.ts — Archivo auxiliar de LIBRERÍA (no visual, no de lógica de
 * negocio propia): solo define los "tipos" (formas de los datos) que se
 * comparten entre el backend, el hook de simulación, el mapa y los
 * controles. Tenerlos en un solo archivo da autocompletado y evita
 * errores de "typos" al leer el JSON del backend en el resto del frontend.
 *
 * ¿Dónde se usa?  Prácticamente en todo el frontend: hooks/useSimulacion.ts,
 * components/Controles.tsx, Mapa/CityMap.tsx y Mapa/geometria.ts importan
 * tipos desde aquí.
 * ============================================================================
 */

// Un punto de entrega (o el depósito, que siempre es el punto con id 0)
export interface Punto {
  id: number;
  x: number; // columna del nodo en la cuadrícula (0..grid_size)
  y: number; // fila del nodo en la cuadrícula (0..grid_size)
}

// Una ruta posible: el orden en que se visitan los puntos y su distancia total
export interface Ruta {
  id: number;
  orden: number[]; // ids de puntos en el orden que se visitan (cierra en el mismo punto de partida)
  distancia: number;
}

// Una "ronda" del modo cuántico simulado: qué rutas se acaban de eliminar
// y cuáles siguen visibles después de esta ronda.
export interface RondaCuantica {
  ronda: number;
  eliminadas_en_esta_ronda: number[];
  visibles: number[];
}

// La respuesta completa del endpoint GET /api/rutas
export interface EscenarioRutas {
  grid_size: number;
  puntos: Punto[];
  rutas: Ruta[];
  mejor_ruta_id: number;
  guion_clasico: number[]; // orden de animación para el modo clásico (una ruta a la vez)
  guion_cuantico: RondaCuantica[]; // guion de animación para el modo cuántico (rondas de eliminación)
  total_rutas: number;
}

// Los dos modos de simulación que el usuario puede disparar
export type ModoSimulacion = "clasico" | "cuantico";

// Estados posibles de la simulación actual (para controlar qué se pinta)
export type EstadoSimulacion =
  | "inactivo" // aún no se ha corrido nada
  | "cargando" // pidiendo datos nuevos al backend
  | "corriendo" // animando rutas
  | "finalizado"; // ya se encontró y se muestra la mejor ruta
