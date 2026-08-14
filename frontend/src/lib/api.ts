/**
 * Cliente del backend.
 *
 * Una sola llamada (`/api/v1/escenario`) trae el mapa y los DOS modos ya
 * resueltos. Esa es la clave del diseño: ambos modos comparten los mismos
 * puntos por construcción, sin que el frontend tenga que coordinar semillas
 * entre peticiones.
 */

import type { Escenario, OpcionesEscenario } from "./tipos";

/**
 * URL del backend FastAPI. Se puede sobreescribir con un `.env.local`:
 *
 *     NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
 */
export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

/** Factorial, para calcular (n-1)! antes de haber pedido nada al backend. */
export function factorial(n: number): number {
  let resultado = 1;
  for (let i = 2; i <= n; i++) resultado *= i;
  return resultado;
}

/**
 * Pide un escenario completo: mapa + traza clásica + traza cuántica.
 *
 * `cache: "no-store"` garantiza que cada llamada sin semilla traiga un mapa
 * recién generado, nunca uno cacheado.
 */
export async function obtenerEscenario(
  opciones: OpcionesEscenario,
): Promise<Escenario> {
  const params = new URLSearchParams({
    n: String(opciones.n),
    cerrada: String(opciones.cerrada),
  });
  if (opciones.orden) params.set("orden", opciones.orden);
  if (opciones.grid_size) params.set("grid_size", String(opciones.grid_size));
  if (opciones.semilla !== undefined && opciones.semilla !== null) {
    params.set("semilla", String(opciones.semilla));
  }

  let respuesta: Response;
  try {
    respuesta = await fetch(`${BACKEND_URL}/api/v1/escenario?${params}`, {
      cache: "no-store",
    });
  } catch {
    // Si el fetch ni siquiera sale, casi siempre es que uvicorn no está arriba.
    throw new Error(
      `No se pudo conectar con el backend en ${BACKEND_URL}. ` +
        `Verifica que siga corriendo: cd backend && python3 -m uvicorn app.main:app --reload --port 8000`,
    );
  }

  if (!respuesta.ok) {
    const detalle = await respuesta.text().catch(() => "");
    throw new Error(
      `El backend respondió ${respuesta.status}. ${detalle.slice(0, 200)}`,
    );
  }

  return respuesta.json();
}
