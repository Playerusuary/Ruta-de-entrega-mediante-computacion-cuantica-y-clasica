/**
 * ============================================================================
 * Auxiliares/api.ts — Archivo auxiliar de LIBRERÍA: la única función de aquí que
 * "hace algo" es pedirle datos al backend (fetch). También vive aquí
 * "factorial", un helper matemático chiquito sin relación con el mapa.
 *
 * ¿Dónde se usa?  hooks/useSimulacion.ts importa "obtenerEscenario" (para
 * traer un escenario nuevo del backend) y "factorial" (para calcular
 * cuántas rutas posibles hay antes de correr la simulación).
 * ============================================================================
 */

import type { EscenarioRutas } from "./tipos";

/** Factorial simple, usado para calcular cuántas rutas hay: (n-1)! */
export function factorial(n: number): number {
  let resultado = 1;
  for (let i = 2; i <= n; i++) resultado *= i;
  return resultado;
}

/**
 * ============================================================================
 * LLAMADA AL BACKEND
 * ============================================================================
 * URL del backend Python (FastAPI). Se puede sobreescribir con una
 * variable de entorno .env.local -> NEXT_PUBLIC_BACKEND_URL=http://...
 * Por defecto se asume que el backend corre en localhost:8000
 * (mientras el frontend Next.js corre en su propio puerto, 3000).
 */
const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

/**
 * Pide al backend un escenario NUEVO y aleatorio: n puntos de entrega
 * (4 o 5), todas sus rutas posibles calculadas, y los "guiones" de
 * animación para el modo clásico y el modo cuántico.
 *
 * cache: "no-store" -> asegura que cada llamada traiga un escenario recién
 * generado (puntos aleatorios), nunca uno guardado en caché.
 */
export async function obtenerEscenario(n: number): Promise<EscenarioRutas> {
  const respuesta = await fetch(`${BACKEND_URL}/api/rutas?n=${n}`, {
    cache: "no-store",
  });

  if (!respuesta.ok) {
    throw new Error(
      `No se pudo obtener el escenario del backend (status ${respuesta.status}). ` +
        `¿Está corriendo "uvicorn app:app --port 8000"?`
    );
  }

  return respuesta.json();
}
