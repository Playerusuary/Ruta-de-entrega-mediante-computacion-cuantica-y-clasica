"use client";

import type { EscenarioRutas, EstadoSimulacion, ModoSimulacion } from "@/Auxiliares/tipos";

/**
 * ============================================================================
 * ControlPanel
 * ============================================================================
 * Replica la fila de botones del Figma:
 *
 *   [Rutas]  [4 Rutas] [5 Rutas]   [Clasico] [Cuantico]   [Posibilidades] [n]
 *
 * - "4 Rutas" / "5 Rutas": eligen cuántos puntos de entrega tendrá el
 *   escenario. El botón elegido se resalta con un contorno azul, el resto
 *   queda neutro.
 *
 * - "Clasico" / "Cuantico": al hacer click, disparan inmediatamente esa
 *   simulación (no son solo "selección", ejecutan el proceso). Se bloquean
 *   mientras una simulación está corriendo para evitar disparar dos
 *   animaciones a la vez.
 *
 * - "Posibilidades": muestra cuántas rutas totales hay para calcular con la
 *   selección actual ( (n-1)! ), aunque todavía no se haya corrido nada.
 */
interface ControlPanelProps {
  numRutas: 4 | 5;
  onSeleccionarNumRutas: (n: 4 | 5) => void;
  modoActivo: ModoSimulacion | null;
  estado: EstadoSimulacion;
  posibilidades: number;
  onIniciar: (modo: ModoSimulacion) => void;
  onReiniciar: () => void;
}

export function ControlPanel({
  numRutas,
  onSeleccionarNumRutas,
  modoActivo,
  estado,
  posibilidades,
  onIniciar,
  onReiniciar,
}: ControlPanelProps) {
  const corriendo = estado === "corriendo" || estado === "cargando";

  return (
    <div className="flex flex-wrap items-end gap-3">
      {/* --- Selector de cantidad de rutas (4 o 5) --- */}
      <CampoEtiquetado etiqueta="Rutas">
        <div className="flex gap-2">
          <BotonOpcion
            texto="4 Rutas"
            activo={numRutas === 4}
            onClick={() => onSeleccionarNumRutas(4)}
            disabled={corriendo}
          />
          <BotonOpcion
            texto="5 Rutas"
            activo={numRutas === 5}
            onClick={() => onSeleccionarNumRutas(5)}
            disabled={corriendo}
          />
        </div>
      </CampoEtiquetado>

      {/* --- Botones que disparan cada algoritmo --- */}
      <button
        onClick={() => onIniciar("clasico")}
        disabled={corriendo}
        className={`px-5 py-2 rounded-md font-semibold text-white transition
          bg-orange-600 hover:bg-orange-500 disabled:opacity-40 disabled:cursor-not-allowed
          ${modoActivo === "clasico" ? "ring-2 ring-offset-2 ring-offset-neutral-900 ring-blue-500" : ""}`}
      >
        Clasico
      </button>

      <button
        onClick={() => onIniciar("cuantico")}
        disabled={corriendo}
        className={`px-5 py-2 rounded-md font-semibold text-white transition
          bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed
          ${modoActivo === "cuantico" ? "ring-2 ring-offset-2 ring-offset-neutral-900 ring-blue-500" : ""}`}
      >
        Cuantico
      </button>

      {/* --- Cuadro con el total de rutas posibles --- */}
      <CampoEtiquetado etiqueta="Posibilidades">
        <div className="min-w-[64px] text-center px-4 py-2 rounded-md bg-neutral-300 text-neutral-900 font-semibold">
          {posibilidades}
        </div>
      </CampoEtiquetado>

      {/* --- Botón para reiniciar: repite la última configuración elegida --- */}
      <button
        onClick={onReiniciar}
        disabled={corriendo}
        title="Vuelve a correr la simulación con la misma configuración (rutas y modo) que se eligió"
        className="px-5 py-2 rounded-md font-semibold text-white transition
          bg-neutral-700 hover:bg-neutral-600 disabled:opacity-40 disabled:cursor-not-allowed
          border border-neutral-500"
      >
        ↻ Reiniciar
      </button>
    </div>
  );
}

/** Envuelve un control con su etiqueta pequeña arriba (como en el Figma). */
function CampoEtiquetado({
  etiqueta,
  children,
}: {
  etiqueta: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs text-neutral-400">{etiqueta}</span>
      {children}
    </div>
  );
}

/** Botón tipo "toggle" usado para 4/5 rutas: contorno azul cuando está activo. */
function BotonOpcion({
  texto,
  activo,
  onClick,
  disabled,
}: {
  texto: string;
  activo: boolean;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-md font-medium transition
        bg-neutral-700 text-white disabled:opacity-40 disabled:cursor-not-allowed
        border-2 ${activo ? "border-blue-500" : "border-transparent"}`}
    >
      {texto}
    </button>
  );
}

/**
 * ============================================================================
 * StatsBar
 * ============================================================================
 * Muestra el "contador de intentos" que pide la actividad:
 *   - Modo clásico: cuántas rutas de las totales ya se probaron.
 *   - Modo cuántico: en qué ronda/iteración de eliminación va.
 * Y al terminar, la distancia de la mejor ruta encontrada.
 */
interface StatsBarProps {
  modoActivo: ModoSimulacion | null;
  estado: EstadoSimulacion;
  contador: number;
  escenario: EscenarioRutas | null;
  rutaGanadoraId: number | null;
}

export function StatsBar({
  modoActivo,
  estado,
  contador,
  escenario,
  rutaGanadoraId,
}: StatsBarProps) {
  if (!modoActivo || estado === "inactivo") {
    return (
      <p className="text-sm text-neutral-400">
        Elige cuántas rutas y luego presiona{" "}
        <span className="text-orange-400 font-medium">Clasico</span> o{" "}
        <span className="text-indigo-400 font-medium">Cuantico</span> para
        iniciar la simulación.
      </p>
    );
  }

  const total =
    modoActivo === "clasico"
      ? escenario?.guion_clasico.length ?? 0
      : escenario?.guion_cuantico.length ?? 0;

  const etiquetaContador = modoActivo === "clasico" ? "Intentos" : "Iteraciones";

  const rutaGanadora =
    rutaGanadoraId !== null
      ? escenario?.rutas.find((r) => r.id === rutaGanadoraId)
      : undefined;

  return (
    <div className="flex flex-wrap items-center gap-4 text-sm">
      <span className="text-neutral-300">
        {etiquetaContador}: <span className="font-semibold text-white">{contador}</span>{" "}
        / {total}
      </span>

      {estado === "cargando" && (
        <span className="text-neutral-400">Generando escenario…</span>
      )}
      {estado === "corriendo" && (
        <span className="text-red-400">Buscando la mejor ruta…</span>
      )}
      {estado === "finalizado" && rutaGanadora && (
        <span className="text-green-400 font-semibold">
          Ruta más corta encontrada — distancia total: {rutaGanadora.distancia}
        </span>
      )}
    </div>
  );
}
