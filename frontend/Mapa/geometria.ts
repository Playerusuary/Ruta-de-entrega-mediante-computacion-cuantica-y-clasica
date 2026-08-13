/**
 * ============================================================================
 * Mapa/geometria.ts — Todo lo necesario para CONVERTIR los datos del
 * backend (puntos y rutas con coordenadas de cuadrícula) en las
 * coordenadas de píxeles y trazos SVG que dibuja Mapa/CityMap.tsx.
 *
 * Nada de este archivo pinta nada en pantalla: solo calcula números y
 * strings de trazo ("d" de un <path>). El que realmente dibuja es
 * Mapa/CityMap.tsx, que importa estas funciones.
 * ============================================================================
 */

import type { Punto, Ruta } from "@/Auxiliares/tipos";

/**
 * ============================================================================
 * GEOMETRÍA DEL MAPA
 * ============================================================================
 * ESPACIADO_NODO: distancia en píxeles entre dos intersecciones seguidas.
 * ANCHO_CALLE: qué tan anchas se ven las calles (el espacio blanco).
 * MARGEN: espacio en blanco entre el borde del SVG y la cuadrícula.
 *
 * El tamaño de cada "manzana" (edificio) se calcula como
 * ESPACIADO_NODO - ANCHO_CALLE, para que las calles queden exactamente
 * ANCHO_CALLE de anchas entre dos edificios.
 */
export const ESPACIADO_NODO = 80;
export const ANCHO_CALLE = 22;
export const MARGEN = 50;

/** Convierte una coordenada de nodo (columna/fila de la cuadrícula) a píxeles del SVG. */
export function nodoAPixeles(punto: { x: number; y: number }) {
  return {
    x: MARGEN + punto.x * ESPACIADO_NODO,
    y: MARGEN + punto.y * ESPACIADO_NODO,
  };
}

/** Tamaño total del lienzo SVG según el tamaño de la cuadrícula (grid_size). */
export function tamanoLienzo(gridSize: number) {
  const lado = MARGEN * 2 + gridSize * ESPACIADO_NODO;
  return { ancho: lado, alto: lado };
}

/**
 * Construye el atributo "d" de un <path> SVG para dibujar una ruta
 * completa siguiendo las calles (nunca en diagonal).
 *
 * Entre cada par de puntos consecutivos se traza una "L": primero
 * se avanza en horizontal hasta alinearse con el siguiente punto, y
 * luego en vertical hasta llegar a él. Esta es una simplificación
 * visual válida porque la distancia que se usa en los cálculos
 * (Manhattan: |dx| + |dy|) es exactamente la misma sin importar si el
 * giro se hace antes o después.
 */
export function construirTrazoRuta(orden: number[], puntosPorId: Map<number, Punto>): string {
  let d = "";

  for (let i = 0; i < orden.length; i++) {
    const punto = puntosPorId.get(orden[i]);
    if (!punto) continue;
    const { x, y } = nodoAPixeles(punto);

    if (i === 0) {
      d += `M ${x} ${y}`;
      continue;
    }

    const anterior = puntosPorId.get(orden[i - 1]);
    if (!anterior) continue;
    const pxAnterior = nodoAPixeles(anterior);

    // Esquina intermedia: mismo x que el punto destino, mismo y que el punto anterior
    // (primero movimiento horizontal, luego vertical)
    d += ` L ${x} ${pxAnterior.y} L ${x} ${y}`;
  }

  return d;
}

/**
 * Etiqueta visible de un punto: convierte el id interno (0..n-1, donde 0
 * siempre es el depósito) a una numeración 1..n para el usuario, donde 1 es
 * siempre el punto de partida/depósito. Así el punto 0 deja de mostrarse
 * como "D" y en su lugar se ve como "1", y los puntos de entrega siguen
 * siendo consecutivos (2, 3, 4, 5...).
 */
export function etiquetaPunto(id: number): string {
  return String(id + 1);
}

/**
 * Un "tramo" (hop) de una ruta: el segmento entre un punto y el siguiente
 * en el orden de visita, junto con los datos necesarios para dibujar una
 * flecha que indique hacia dónde se avanza en ese tramo.
 */
export interface TramoRuta {
  d: string; // "d" del <path> de solo este tramo (con su giro en L)
  puntoMedio: { x: number; y: number }; // dónde poner la flecha
  angulo: number; // grados, dirección de avance en ese tramo
}

/**
 * Descompone una ruta completa en sus tramos individuales (un tramo por
 * cada "salto" entre dos puntos consecutivos del orden de visita). Se usa
 * para dibujar una flecha de dirección sobre cada tramo, de forma que se
 * vea con claridad en qué orden se recorren los puntos.
 */
export function construirTramosRuta(
  orden: number[],
  puntosPorId: Map<number, Punto>
): TramoRuta[] {
  const tramos: TramoRuta[] = [];

  for (let i = 1; i < orden.length; i++) {
    const desde = puntosPorId.get(orden[i - 1]);
    const hasta = puntosPorId.get(orden[i]);
    if (!desde || !hasta) continue;

    const pxDesde = nodoAPixeles(desde);
    const pxHasta = nodoAPixeles(hasta);
    const esquina = { x: pxHasta.x, y: pxDesde.y };

    const d = `M ${pxDesde.x} ${pxDesde.y} L ${esquina.x} ${esquina.y} L ${pxHasta.x} ${pxHasta.y}`;

    // La flecha se coloca a mitad del último sub-tramo (el que realmente
    // llega al punto destino) para que apunte "entrando" a ese punto. Si
    // ese sub-tramo tiene longitud 0 (el giro ya cayó sobre el destino),
    // se usa el primer sub-tramo en su lugar.
    let dirX = pxHasta.x - esquina.x;
    let dirY = pxHasta.y - esquina.y;
    let puntoMedio = { x: (esquina.x + pxHasta.x) / 2, y: (esquina.y + pxHasta.y) / 2 };

    if (dirX === 0 && dirY === 0) {
      dirX = esquina.x - pxDesde.x;
      dirY = esquina.y - pxDesde.y;
      puntoMedio = { x: (pxDesde.x + esquina.x) / 2, y: (pxDesde.y + esquina.y) / 2 };
    }

    const angulo = (Math.atan2(dirY, dirX) * 180) / Math.PI;

    tramos.push({ d, puntoMedio, angulo });
  }

  return tramos;
}

/** Índice rápido de puntos por id, útil para no buscar en el arreglo cada vez. */
export function indexarPuntos(puntos: Punto[]): Map<number, Punto> {
  return new Map(puntos.map((p) => [p.id, p]));
}

/** Índice rápido de rutas por id. */
export function indexarRutas(rutas: Ruta[]): Map<number, Ruta> {
  return new Map(rutas.map((r) => [r.id, r]));
}
