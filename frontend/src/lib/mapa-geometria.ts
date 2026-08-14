/**
 * Convierte los datos del backend (coordenadas de cuadrícula) en píxeles y
 * trazos SVG. Nada de aquí pinta: solo calcula números y strings de `path`.
 * El que dibuja es `components/CityMap.tsx`.
 *
 * Portado de `Mapa/geometria.ts` de la rama del compañero.
 */

import type { Punto, Ruta } from "./tipos";

/** Distancia en píxeles entre dos intersecciones seguidas. */
export const ESPACIADO_NODO = 80;
/** Qué tan anchas se ven las calles. */
export const ANCHO_CALLE = 22;
/** Espacio entre el borde del SVG y la cuadrícula. */
export const MARGEN = 50;

/** Convierte una coordenada de nodo (columna/fila) a píxeles del SVG. */
export function nodoAPixeles(punto: { x: number; y: number }) {
  return {
    x: MARGEN + punto.x * ESPACIADO_NODO,
    y: MARGEN + punto.y * ESPACIADO_NODO,
  };
}

/** Tamaño total del lienzo según `grid_size`. */
export function tamanoLienzo(gridSize: number) {
  const lado = MARGEN * 2 + gridSize * ESPACIADO_NODO;
  return { ancho: lado, alto: lado };
}

/**
 * Construye el atributo `d` de un `<path>` para dibujar una ruta completa
 * siguiendo las calles, nunca en diagonal.
 *
 * Entre cada par de puntos se traza una "L": primero horizontal hasta
 * alinearse con el destino, luego vertical hasta llegar. Es una simplificación
 * visual válida porque la distancia Manhattan (|dx| + |dy|) es idéntica sin
 * importar dónde se dé el giro.
 */
export function construirTrazoRuta(
  orden: number[],
  puntosPorId: Map<number, Punto>,
): string {
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

    d += ` L ${x} ${pxAnterior.y} L ${x} ${y}`;
  }

  return d;
}

/** Un tramo de ruta, con lo necesario para dibujarle una flecha de dirección. */
export interface TramoRuta {
  d: string;
  puntoMedio: { x: number; y: number };
  /** Grados; dirección de avance en ese tramo. */
  angulo: number;
}

/**
 * Descompone una ruta en sus tramos individuales, uno por cada salto entre
 * puntos consecutivos, para poder dibujar una flecha sobre cada uno y que se
 * lea el orden del recorrido.
 */
export function construirTramosRuta(
  orden: number[],
  puntosPorId: Map<number, Punto>,
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

    // La flecha va a mitad del último sub-tramo, el que entra al destino. Si
    // ese sub-tramo mide 0 (el giro cayó sobre el destino), se usa el primero.
    let dirX = pxHasta.x - esquina.x;
    let dirY = pxHasta.y - esquina.y;
    let puntoMedio = {
      x: (esquina.x + pxHasta.x) / 2,
      y: (esquina.y + pxHasta.y) / 2,
    };

    if (dirX === 0 && dirY === 0) {
      dirX = esquina.x - pxDesde.x;
      dirY = esquina.y - pxDesde.y;
      puntoMedio = {
        x: (pxDesde.x + esquina.x) / 2,
        y: (pxDesde.y + esquina.y) / 2,
      };
    }

    tramos.push({
      d,
      puntoMedio,
      angulo: (Math.atan2(dirY, dirX) * 180) / Math.PI,
    });
  }

  return tramos;
}

/**
 * Traduce la probabilidad de una ruta a opacidad de trazo.
 *
 * No es lineal a propósito. Con 24 rutas en superposición, la probabilidad
 * inicial es 1/24 = 0.042: dibujarlas a esa opacidad las haría invisibles, y a
 * opacidad plena serían una maraña. La raíz cuadrada las deja
 * semi-transparentes al inicio (~0.25) y hace que la ganadora destaque con
 * claridad conforme se amplifica, que es justo el efecto que pide el enunciado.
 */
export function probabilidadAOpacidad(probabilidad: number): number {
  const p = Math.max(0, Math.min(1, probabilidad));
  return 0.05 + 0.95 * Math.sqrt(p);
}

/** Índice de puntos por id, para no recorrer el arreglo en cada dibujo. */
export function indexarPuntos(puntos: Punto[]): Map<number, Punto> {
  return new Map(puntos.map((p) => [p.id, p]));
}

/** Índice de rutas por id. */
export function indexarRutas(rutas: Ruta[]): Map<number, Ruta> {
  return new Map(rutas.map((r) => [r.id, r]));
}
