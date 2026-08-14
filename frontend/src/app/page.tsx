"use client";

import CityMap from "@/components/CityMap";
import { BarraEstado, PanelControl } from "@/components/Controles";
import { useSimulacion } from "@/hooks/useSimulacion";

export default function Home() {
  const s = useSimulacion();

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-6 py-10">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Ruta de entrega — clásica vs cuántica
        </h1>
        <p className="text-sm text-neutral-400">
          Mini TSP sobre una ciudad en cuadrícula. El modo clásico prueba una
          ruta a la vez; el cuántico las mantiene todas en superposición y
          amplifica la mejor.
        </p>
      </header>

      <PanelControl
        n={s.n}
        cerrada={s.cerrada}
        corriendo={s.corriendo}
        posibilidades={s.posibilidades}
        modoActivo={s.modoActivo}
        onCambiarN={s.cambiarN}
        onCambiarCerrada={s.cambiarCerrada}
        onIniciar={s.iniciar}
        onNuevoMapa={s.nuevoMapa}
      />

      {s.error && (
        <div className="rounded-md border border-red-800 bg-red-950/60 px-4 py-3 text-sm text-red-200">
          <p className="font-semibold">No se pudo cargar el escenario</p>
          <p className="mt-1 text-red-300/90">{s.error}</p>
        </div>
      )}

      <BarraEstado
        escenario={s.escenario}
        modoActivo={s.modoActivo}
        estado={s.estado}
        contador={s.contador}
        totalFrames={s.totalFrames}
        pasoClasico={s.pasoClasico}
        pasoCuantico={s.pasoCuantico}
        rutaGanadora={s.rutaGanadora}
      />

      <CityMap
        escenario={s.escenario}
        rutaClasicaId={s.rutaClasicaId}
        mejorParcial={s.mejorParcial}
        probabilidades={s.probabilidades}
        rutaGanadora={s.rutaGanadora}
      />

      <Leyenda />

      {s.escenario && <Comparacion escenario={s.escenario} />}
    </main>
  );
}

function Leyenda() {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-neutral-400">
      <Muestra color="#3b82f6" texto="Base (depósito)" />
      <Muestra color="#ef4444" texto="Ruta en evaluación / superposición" />
      <Muestra color="#f59e0b" texto="Mejor hasta ahora" />
      <Muestra color="#22c55e" texto="Ruta ganadora" />
    </div>
  );
}

function Muestra({ color, texto }: { color: string; texto: string }) {
  return (
    <span className="flex items-center gap-2">
      <span
        className="inline-block h-1 w-6 rounded"
        style={{ backgroundColor: color }}
      />
      {texto}
    </span>
  );
}

/** El titular del proyecto: cuánto le costó a cada modo llegar al mismo lugar. */
function Comparacion({
  escenario,
}: {
  escenario: NonNullable<ReturnType<typeof useSimulacion>["escenario"]>;
}) {
  const { clasico, cuantico } = escenario;

  return (
    <section className="grid gap-4 sm:grid-cols-2">
      <Tarjeta
        titulo="Clásico (bit)"
        acento="text-orange-400"
        filas={[
          ["Rutas evaluadas", String(clasico.rutas_evaluadas)],
          ["Distancia mínima", String(clasico.mejor_distancia)],
          ["Empates en la mínima", String(clasico.empates_en_la_mejor.length)],
        ]}
      />
      <Tarjeta
        titulo="Cuántico (qubit)"
        acento="text-indigo-400"
        filas={[
          ["Iteraciones", String(cuantico.iteraciones)],
          ["Distancia medida", String(cuantico.medicion_distancia)],
          [
            "Confianza final",
            `${(cuantico.probabilidad_final_marcadas * 100).toFixed(1)}%`,
          ],
        ]}
      />
    </section>
  );
}

function Tarjeta({
  titulo,
  acento,
  filas,
}: {
  titulo: string;
  acento: string;
  filas: [string, string][];
}) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900/60 p-4">
      <h2 className={`mb-3 text-sm font-semibold ${acento}`}>{titulo}</h2>
      <dl className="flex flex-col gap-1.5 text-sm">
        {filas.map(([clave, valor]) => (
          <div key={clave} className="flex justify-between gap-4">
            <dt className="text-neutral-400">{clave}</dt>
            <dd className="font-semibold tabular-nums text-neutral-100">
              {valor}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
