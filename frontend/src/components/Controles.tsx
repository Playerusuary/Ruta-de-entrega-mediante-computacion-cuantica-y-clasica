"use client";

import type {
  Escenario,
  EstadoSimulacion,
  ModoSimulacion,
  PasoClasico,
  PasoCuantico,
} from "@/lib/tipos";

/**
 * Panel de control y barra de estado. Portado de `components/Controles.tsx` de
 * la rama del compañero, con el control de ruta cerrada que expone nuestro
 * backend.
 *
 * La distancia es siempre Manhattan y no es configurable: la ciudad es una
 * cuadrícula y el vehículo circula por las calles, así que no tendría sentido
 * ofrecer una métrica que le permita cortar en diagonal.
 */

interface PanelProps {
  n: 4 | 5;
  cerrada: boolean;
  corriendo: boolean;
  posibilidades: number;
  modoActivo: ModoSimulacion | null;
  onCambiarN: (n: 4 | 5) => void;
  onCambiarCerrada: (v: boolean) => void;
  onIniciar: (modo: ModoSimulacion) => void;
  onNuevoMapa: () => void;
}

export function PanelControl({
  n,
  cerrada,
  corriendo,
  posibilidades,
  modoActivo,
  onCambiarN,
  onCambiarCerrada,
  onIniciar,
  onNuevoMapa,
}: PanelProps) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <Campo etiqueta="Puntos">
        <div className="flex gap-2">
          <BotonOpcion
            texto="4"
            activo={n === 4}
            onClick={() => onCambiarN(4)}
            disabled={corriendo}
          />
          <BotonOpcion
            texto="5"
            activo={n === 5}
            onClick={() => onCambiarN(5)}
            disabled={corriendo}
          />
        </div>
      </Campo>

      <Campo etiqueta="Ruta">
        <BotonOpcion
          texto={cerrada ? "Regresa a la base" : "No regresa"}
          activo={cerrada}
          onClick={() => onCambiarCerrada(!cerrada)}
          disabled={corriendo}
        />
      </Campo>

      <Campo etiqueta="Simular">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onIniciar("clasico")}
            disabled={corriendo}
            className={`rounded-md bg-orange-600 px-5 py-2 font-semibold text-white transition hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-40 ${
              modoActivo === "clasico"
                ? "ring-2 ring-blue-500 ring-offset-2 ring-offset-neutral-950"
                : ""
            }`}
          >
            Clásico
          </button>
          <button
            type="button"
            onClick={() => onIniciar("cuantico")}
            disabled={corriendo}
            className={`rounded-md bg-indigo-600 px-5 py-2 font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40 ${
              modoActivo === "cuantico"
                ? "ring-2 ring-blue-500 ring-offset-2 ring-offset-neutral-950"
                : ""
            }`}
          >
            Cuántico
          </button>
        </div>
      </Campo>

      <Campo etiqueta="Rutas posibles">
        <div className="min-w-[64px] rounded-md bg-neutral-300 px-4 py-2 text-center font-semibold text-neutral-900">
          {posibilidades}
        </div>
      </Campo>

      <button
        type="button"
        onClick={onNuevoMapa}
        disabled={corriendo}
        title="Genera un mapa nuevo con puntos aleatorios"
        className="rounded-md border border-neutral-600 bg-neutral-800 px-5 py-2 font-semibold text-white transition hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-40"
      >
        ↻ Nuevo mapa
      </button>
    </div>
  );
}

function Campo({
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
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`rounded-md border-2 bg-neutral-800 px-4 py-2 font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-40 ${
        activo
          ? "border-blue-500"
          : "border-transparent hover:border-neutral-600"
      }`}
    >
      {texto}
    </button>
  );
}

/**
 * Barra de estado. Muestra el contador que pide la actividad: rutas evaluadas
 * en clásico, iteraciones en cuántico.
 */
interface BarraProps {
  escenario: Escenario | null;
  modoActivo: ModoSimulacion | null;
  estado: EstadoSimulacion;
  contador: number;
  totalFrames: number;
  pasoClasico: PasoClasico | null;
  pasoCuantico: PasoCuantico | null;
  rutaGanadora: number[] | null;
}

export function BarraEstado({
  escenario,
  modoActivo,
  estado,
  contador,
  totalFrames,
  pasoClasico,
  pasoCuantico,
  rutaGanadora,
}: BarraProps) {
  if (estado === "cargando") {
    return <p className="text-sm text-neutral-400">Generando escenario…</p>;
  }

  if (!modoActivo) {
    return (
      <p className="text-sm text-neutral-400">
        Presiona <span className="font-medium text-orange-400">Clásico</span> o{" "}
        <span className="font-medium text-indigo-400">Cuántico</span> para
        animar la búsqueda. Los dos corren sobre este mismo mapa.
      </p>
    );
  }

  const etiqueta = modoActivo === "clasico" ? "Rutas evaluadas" : "Iteración";

  return (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
      <span className="text-neutral-300">
        {etiqueta}:{" "}
        <span className="font-semibold text-white tabular-nums">
          {contador}
        </span>
        <span className="text-neutral-500"> / {totalFrames}</span>
      </span>

      {/* Datos del frame en curso. Al finalizar desaparecen: el mapa ya solo
          muestra la ganadora, y seguir enseñando "esta ruta" lo contradiría. */}
      {estado === "corriendo" && modoActivo === "clasico" && pasoClasico && (
        <>
          <span className="text-neutral-300">
            Esta ruta:{" "}
            <span className="font-semibold text-red-400 tabular-nums">
              {pasoClasico.distancia}
            </span>
          </span>
          <span className="text-neutral-300">
            Mejor hasta ahora:{" "}
            <span className="font-semibold text-amber-400 tabular-nums">
              {pasoClasico.mejor_distancia}
            </span>
          </span>
        </>
      )}

      {estado === "corriendo" && modoActivo === "cuantico" && pasoCuantico && (
        <span className="text-neutral-300">
          Confianza:{" "}
          <span className="font-semibold text-indigo-300 tabular-nums">
            {(pasoCuantico.probabilidad_marcadas * 100).toFixed(1)}%
          </span>
        </span>
      )}

      {estado === "corriendo" && (
        <span className="text-neutral-400">Buscando…</span>
      )}

      {estado === "finalizado" && rutaGanadora && escenario && (
        <span className="font-semibold text-green-400">
          {modoActivo === "clasico"
            ? `Ruta más corta: ${escenario.clasico.mejor_distancia}`
            : `Medición: ${escenario.cuantico.medicion_distancia}${
                escenario.cuantico.acerto ? " — acertó" : " — falló"
              }`}
        </span>
      )}
    </div>
  );
}
