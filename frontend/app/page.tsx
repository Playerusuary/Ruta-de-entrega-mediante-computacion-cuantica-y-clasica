"use client";

import CityMap from "@/Mapa/CityMap";
import { ControlPanel, StatsBar } from "@/components/Controles";
import { useSimulacion } from "@/hooks/useSimulacion";

/**
 * ============================================================================
 * ★★★ ESTA ES LA VISTA / PÁGINA PRINCIPAL DE LA APLICACIÓN ★★★
 * ============================================================================
 * "app/page.tsx" es el archivo que Next.js dibuja en http://localhost:3000
 * (la ruta "/"). Next.js exige que se llame exactamente "page.tsx" y que
 * viva dentro de "app/" — por eso no se movió ni se renombró junto con el
 * resto de las carpetas.
 *
 * Este componente NO tiene lógica propia: solo conecta el hook
 * "useSimulacion" (que trae los datos del backend y maneja la animación)
 * con los componentes visuales (ControlPanel, StatsBar y CityMap, este
 * último ahora dentro de la carpeta "Mapa/").
 *
 * Es un Client Component ("use client") porque usa estado de React y
 * temporizadores (setInterval) para animar, cosas que solo pueden vivir
 * en el navegador, no en el servidor de Next.js.
 *
 * Guía rápida del resto de "frontend/" (ver también README.md):
 *   Mapa/        -> todo lo que dibuja el mapa (CityMap.tsx + geometria.ts)
 *   components/  -> Controles.tsx: botones y barra de estadísticas
 *   hooks/       -> useSimulacion.ts: el "cerebro" de la simulación
 *   Auxiliares/  -> librerías auxiliares: tipos.ts y api.ts
 * ============================================================================
 */
export default function Home() {
  const {
    numRutas,
    seleccionarNumRutas,
    escenario,
    modoActivo,
    estado,
    error,
    rutaVisibleClasicoId,
    rutasVisiblesCuantico,
    rutaGanadoraId,
    contador,
    posibilidades,
    iniciarSimulacion,
    reiniciar,
  } = useSimulacion();

  return (
    <main className="min-h-screen bg-neutral-950 text-white px-6 py-8 sm:px-10">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        {/* --- Título y descripción (texto tal cual del Figma) --- */}
        <header className="flex flex-col gap-2">
          <h1 className="text-2xl sm:text-3xl font-bold">
            Simulacion de programa de rutas de entrega mediante computacion
            clasica y cuantica
          </h1>
          <p className="text-neutral-300 max-w-3xl">
            Se desarrollo un programa con el cual facilita la entrega de
            paquetes mediante rutas y aumenta la efectividad de traslado
            buscando la mejor ruta posible entre diferentes posibilidades.
          </p>
        </header>

        {/* --- Panel de controles --- */}
        <ControlPanel
          numRutas={numRutas}
          onSeleccionarNumRutas={seleccionarNumRutas}
          modoActivo={modoActivo}
          estado={estado}
          posibilidades={posibilidades}
          onIniciar={iniciarSimulacion}
          onReiniciar={reiniciar}
        />

        {/* --- Contador / estado de la simulación --- */}
        <StatsBar
          modoActivo={modoActivo}
          estado={estado}
          contador={contador}
          escenario={escenario}
          rutaGanadoraId={rutaGanadoraId}
        />

        {/* Banner de error bien visible: casi siempre indica que el backend
            (uvicorn) no está corriendo o no se puede alcanzar. */}
        {error && (
          <div className="rounded-md border border-red-500 bg-red-950/60 px-4 py-3 text-sm text-red-300">
            ⚠ {error}
          </div>
        )}

        {/* --- Mapa de la ciudad con la animación de rutas --- */}
        <div className="bg-neutral-900 rounded-lg p-4 border border-neutral-800">
          <CityMap
            escenario={escenario}
            rutaVisibleClasicoId={rutaVisibleClasicoId}
            rutasVisiblesCuantico={rutasVisiblesCuantico}
            rutaGanadoraId={rutaGanadoraId}
          />
        </div>
      </div>
    </main>
  );
}
