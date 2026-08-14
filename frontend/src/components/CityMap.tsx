"use client";

import { useMemo } from "react";
import {
  ANCHO_CALLE,
  construirTramosRuta,
  construirTrazoRuta,
  ESPACIADO_NODO,
  indexarPuntos,
  indexarRutas,
  nodoAPixeles,
  probabilidadAOpacidad,
  tamanoLienzo,
} from "@/lib/mapa-geometria";
import type { Escenario, ProbabilidadRuta, Punto } from "@/lib/tipos";

/**
 * El mapa de la ciudad. Portado de `Mapa/CityMap.tsx` de la rama del compañero.
 *
 * Dibuja la cuadrícula (calles + edificios), los puntos de entrega y las rutas
 * encima. NO calcula nada: recibe todo ya resuelto por el backend.
 *
 * Los dos modos se ven distinto a propósito, y esa diferencia ES el proyecto:
 *
 *   - Clásico: UNA ruta visible a la vez, en rojo. Un bit está en un solo
 *     estado a la vez.
 *   - Cuántico: TODAS las rutas a la vez, con la opacidad de cada una atada a
 *     su probabilidad. Eso es la superposición.
 */

interface Props {
  escenario: Escenario | null;
  /** Modo clásico: la única ruta visible en este frame. */
  rutaClasicaId: number | null;
  /** Modo clásico: la campeona vigente, al fondo. */
  mejorParcial: number[] | null;
  /** Modo cuántico: probabilidad de todas las rutas en este frame. */
  probabilidades: ProbabilidadRuta[] | null;
  /** Ruta ganadora final, en verde por encima de todo. */
  rutaGanadora: number[] | null;
}

const ROJO = "#ef4444";
const VERDE = "#22c55e";
const AMBAR = "#f59e0b";

export default function CityMap({
  escenario,
  rutaClasicaId,
  mejorParcial,
  probabilidades,
  rutaGanadora,
}: Props) {
  // Sin escenario mostramos una cuadrícula vacía del tamaño por default para
  // que el layout no salte cuando lleguen los datos.
  const gridSize = escenario?.grid_size ?? 6;
  const { ancho, alto } = tamanoLienzo(gridSize);

  const puntosPorId = useMemo(
    () =>
      escenario ? indexarPuntos(escenario.puntos) : new Map<number, Punto>(),
    [escenario],
  );
  const rutasPorId = useMemo(
    () => (escenario ? indexarRutas(escenario.rutas) : new Map()),
    [escenario],
  );

  const edificios = useMemo(() => {
    const lista: { x: number; y: number }[] = [];
    for (let col = 0; col < gridSize; col++) {
      for (let fila = 0; fila < gridSize; fila++) {
        lista.push({ x: col, y: fila });
      }
    }
    return lista;
  }, [gridSize]);

  const rutaClasica =
    rutaClasicaId !== null ? rutasPorId.get(rutaClasicaId) : undefined;

  return (
    <div className="w-full flex justify-center">
      <svg
        viewBox={`0 0 ${ancho} ${alto}`}
        width="100%"
        style={{ maxWidth: ancho }}
        className="rounded-lg"
        role="img"
        aria-label="Mapa de la ciudad con las rutas de entrega"
      >
        {/* Fondo = calles */}
        <rect x={0} y={0} width={ancho} height={alto} fill="#f5f5f5" />

        {/* Edificios */}
        {edificios.map((b) => {
          const esquina = nodoAPixeles(b);
          const tamano = ESPACIADO_NODO - ANCHO_CALLE;
          return (
            <rect
              key={`${b.x}-${b.y}`}
              x={esquina.x + ANCHO_CALLE / 2}
              y={esquina.y + ANCHO_CALLE / 2}
              width={tamano}
              height={tamano}
              fill="#3a3a3a"
              rx={3}
            />
          );
        })}

        {/* Contorno */}
        <rect
          x={2}
          y={2}
          width={ancho - 4}
          height={alto - 4}
          fill="none"
          stroke="#1a1a1a"
          strokeWidth={4}
        />

        {/* ---- MODO CUANTICO: todas las rutas a la vez ----
            La opacidad sale de la probabilidad real de cada ruta, así que las
            malas se desvanecen solas conforme avanza la amplificación. */}
        {probabilidades?.map((pr) => {
          const ruta = rutasPorId.get(pr.ruta_id);
          if (!ruta) return null;
          const opacidad = probabilidadAOpacidad(pr.probabilidad);
          return (
            <path
              key={`q-${pr.ruta_id}`}
              d={construirTrazoRuta(ruta.orden, puntosPorId)}
              fill="none"
              stroke={ROJO}
              strokeWidth={3 + 4 * pr.probabilidad}
              strokeOpacity={opacidad}
              strokeLinecap="round"
            />
          );
        })}

        {/* ---- MODO CLASICO: la campeona vigente, tenue al fondo ---- */}
        {mejorParcial && (
          <path
            d={construirTrazoRuta(mejorParcial, puntosPorId)}
            fill="none"
            stroke={AMBAR}
            strokeWidth={5}
            strokeOpacity={0.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* ---- MODO CLASICO: la ruta que se está probando ahora ---- */}
        {rutaClasica && (
          <RutaConFlechas
            orden={rutaClasica.orden}
            puntosPorId={puntosPorId}
            color={ROJO}
            grosor={5}
          />
        )}

        {/* ---- Ganadora final, por encima de todo ---- */}
        {rutaGanadora && (
          <RutaConFlechas
            orden={rutaGanadora}
            puntosPorId={puntosPorId}
            color={VERDE}
            grosor={6}
          />
        )}

        {/* ---- Puntos de entrega ---- */}
        {escenario?.puntos.map((p) => {
          const { x, y } = nodoAPixeles(p);
          const esDeposito = p.id === 0;
          return (
            <g key={p.id}>
              <circle
                cx={x}
                cy={y}
                r={esDeposito ? 14 : 12}
                fill={esDeposito ? "#3b82f6" : "#ffffff"}
                stroke="#1a1a1a"
                strokeWidth={2}
              />
              <text
                x={x}
                y={y + 4}
                textAnchor="middle"
                fontSize={11}
                fontWeight="bold"
                fill={esDeposito ? "#ffffff" : "#1a1a1a"}
              >
                {p.etiqueta || String(p.id)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/** Una ruta con flechitas de dirección sobre cada tramo. */
function RutaConFlechas({
  orden,
  puntosPorId,
  color,
  grosor,
}: {
  orden: number[];
  puntosPorId: Map<number, Punto>;
  color: string;
  grosor: number;
}) {
  const tramos = useMemo(
    () => construirTramosRuta(orden, puntosPorId),
    [orden, puntosPorId],
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
          // biome-ignore lint/suspicious/noArrayIndexKey: los tramos son posicionales
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
