"use client";

import { useMemo } from "react";
import {
  ANCHO_CALLE,
  ESPACIADO_NODO,
  construirTramosRuta,
  construirTrazoRuta,
  etiquetaPunto,
  indexarPuntos,
  indexarRutas,
  nodoAPixeles,
  tamanoLienzo,
} from "./geometria";
import type { EscenarioRutas } from "@/Auxiliares/tipos";

interface Props {
  escenario: EscenarioRutas | null;
  // Modo clásico: una sola ruta visible (roja mientras corre)
  rutaVisibleClasicoId: number | null;
  // Modo cuántico: varias rutas visibles a la vez (semi-transparentes)
  rutasVisiblesCuantico: number[];
  // Ruta ganadora final (se pinta en verde)
  rutaGanadoraId: number | null;
}

/**
 * ============================================================================
 * Mapa/CityMap.tsx
 * ============================================================================
 * Este archivo vive en la carpeta "Mapa" junto con "geometria.ts": aquí
 * están TODOS los componentes necesarios para crear y dibujar el mapa
 * de la ciudad (calles, edificios, puntos de entrega y rutas animadas).
 * ============================================================================
 * Dibuja:
 *   1. El fondo blanco = las calles.
 *   2. Un bloque gris oscuro por cada "manzana" = los edificios.
 *   3. Un contorno (borde) alrededor de todo el mapa.
 *   4. Los puntos de entrega (círculos), con el punto 0 = depósito destacado.
 *   5. Las rutas encima, como líneas que solo se mueven en horizontal/vertical
 *      (nunca en diagonal, porque el auto va por las calles).
 *
 * Este componente NO calcula nada (ni distancias ni rutas): solo recibe los
 * datos ya calculados por el backend (o por el hook useSimulacion) y los pinta.
 */
export default function CityMap({
  escenario,
  rutaVisibleClasicoId,
  rutasVisiblesCuantico,
  rutaGanadoraId,
}: Props) {
  // Mientras no haya un escenario cargado, mostramos un mapa "vacío" de
  // tamaño por default (grid de 6x6) para que la pantalla no salte de tamaño.
  const gridSize = escenario?.grid_size ?? 6;
  const { ancho, alto } = tamanoLienzo(gridSize);

  const puntosPorId = useMemo(
    () => (escenario ? indexarPuntos(escenario.puntos) : new Map()),
    [escenario]
  );
  const rutasPorId = useMemo(
    () => (escenario ? indexarRutas(escenario.rutas) : new Map()),
    [escenario]
  );

  // Genera los rectángulos de los edificios (uno por cada celda de la cuadrícula)
  const edificios = useMemo(() => {
    const lista: { x: number; y: number }[] = [];
    for (let col = 0; col < gridSize; col++) {
      for (let fila = 0; fila < gridSize; fila++) {
        lista.push({ x: col, y: fila });
      }
    }
    return lista;
  }, [gridSize]);

  return (
    <div className="w-full flex justify-center">
      <svg
        viewBox={`0 0 ${ancho} ${alto}`}
        width="100%"
        style={{ maxWidth: ancho }}
        className="rounded-md"
      >
        {/* Fondo = calles (blanco) */}
        <rect x={0} y={0} width={ancho} height={alto} fill="#f5f5f5" />

        {/* Edificios = gris oscuro, con un pequeño margen para dejar ver la calle */}
        {edificios.map((b, i) => {
          const esquina = nodoAPixeles(b);
          const tamano = ESPACIADO_NODO - ANCHO_CALLE;
          return (
            <rect
              key={i}
              x={esquina.x + ANCHO_CALLE / 2}
              y={esquina.y + ANCHO_CALLE / 2}
              width={tamano}
              height={tamano}
              fill="#3a3a3a"
              rx={3}
            />
          );
        })}

        {/* Contorno del mapa */}
        <rect
          x={2}
          y={2}
          width={ancho - 4}
          height={alto - 4}
          fill="none"
          stroke="#1a1a1a"
          strokeWidth={4}
        />

        {/* ------- RUTAS ------- */}

        {/* Modo cuántico: todas las rutas que siguen visibles, semi-transparentes
            y PARPADEANDO (simboliza que todavía están "en superposición", sin
            que se sepa aún cuál va a sobrevivir). */}
        {rutasVisiblesCuantico.map((rutaId) => {
          const ruta = rutasPorId.get(rutaId);
          if (!ruta) return null;
          return (
            <path
              key={`q-${rutaId}`}
              className="animate-pulse"
              d={construirTrazoRuta(ruta.orden, puntosPorId)}
              fill="none"
              stroke="#ef4444" // rojo
              strokeWidth={4}
              strokeOpacity={0.35}
              strokeLinecap="round"
            />
          );
        })}

        {/* Modo clásico: una sola ruta visible, en rojo, mientras se está probando,
            con flechas que muestran en qué orden se recorren los puntos */}
        {rutaVisibleClasicoId !== null &&
          (() => {
            const ruta = rutasPorId.get(rutaVisibleClasicoId);
            if (!ruta) return null;
            return (
              <RutaConFlechas
                orden={ruta.orden}
                puntosPorId={puntosPorId}
                color="#ef4444" // rojo
                grosor={5}
              />
            );
          })()}

        {/* Ruta ganadora final, en verde, por encima de todo lo demás, con
            flechas de dirección para que se entienda el orden de recorrido:
            1 (depósito) -> ... -> vuelta a 1. */}
        {rutaGanadoraId !== null &&
          (() => {
            const ruta = rutasPorId.get(rutaGanadoraId);
            if (!ruta) return null;
            return (
              <RutaConFlechas
                orden={ruta.orden}
                puntosPorId={puntosPorId}
                color="#22c55e" // verde
                grosor={6}
              />
            );
          })()}

        {/* ------- PUNTOS DE ENTREGA ------- */}
        {escenario?.puntos.map((p) => {
          const { x, y } = nodoAPixeles(p);
          const esDeposito = p.id === 0;
          return (
            <g key={p.id}>
              <circle
                cx={x}
                cy={y}
                r={esDeposito ? 13 : 11}
                fill={esDeposito ? "#3b82f6" : "#ffffff"}
                stroke="#1a1a1a"
                strokeWidth={2}
              />
              <text
                x={x}
                y={y + 4}
                textAnchor="middle"
                fontSize={12}
                fontWeight="bold"
                fill={esDeposito ? "#ffffff" : "#1a1a1a"}
              >
                {etiquetaPunto(p.id)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/**
 * Dibuja una ruta completa (el trazo grueso de color) MÁS una flechita
 * pequeña sobre cada tramo, apuntando hacia el punto al que se llega. Con
 * esto se ve, de un vistazo, el orden en que se recorren los puntos:
 * "1 -> 2 -> 3 -> ... -> 1" en vez de solo una línea sin dirección.
 */
function RutaConFlechas({
  orden,
  puntosPorId,
  color,
  grosor,
}: {
  orden: number[];
  puntosPorId: Map<number, { id: number; x: number; y: number }>;
  color: string;
  grosor: number;
}) {
  const tramos = useMemo(
    () => construirTramosRuta(orden, puntosPorId),
    [orden, puntosPorId]
  );

  const TAMANO_FLECHA = 7;

  return (
    <g>
      <path
        d={construirTrazoRuta(orden, puntosPorId)}
        fill="none"
        stroke={color}
        strokeWidth={grosor}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {tramos.map((tramo, i) => (
        <polygon
          key={i}
          points={`0,-${TAMANO_FLECHA * 0.65} ${TAMANO_FLECHA},0 0,${TAMANO_FLECHA * 0.65}`}
          fill={color}
          stroke="#1a1a1a"
          strokeWidth={1}
          transform={`translate(${tramo.puntoMedio.x}, ${tramo.puntoMedio.y}) rotate(${tramo.angulo})`}
        />
      ))}
    </g>
  );
}
