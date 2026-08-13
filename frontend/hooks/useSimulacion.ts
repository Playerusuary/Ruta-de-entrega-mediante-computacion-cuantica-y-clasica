"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { factorial, obtenerEscenario } from "@/Auxiliares/api";
import type {
  EscenarioRutas,
  EstadoSimulacion,
  ModoSimulacion,
} from "@/Auxiliares/tipos";

/**
 * ============================================================================
 * HOOK useSimulacion
 * ============================================================================
 * Aquí vive TODA la lógica de la aplicación:
 *
 * 1. Guarda cuántos puntos de entrega eligió el usuario (4 o 5).
 * 2. Pide al backend un escenario (puntos + todas las rutas + guiones de
 *    animación) cada vez que el usuario dispara el modo clásico o cuántico.
 * 3. Reproduce el guion correspondiente usando setInterval, actualizando
 *    en cada "tick" qué ruta(s) se deben pintar en el mapa.
 * 4. Expone contadores (intentos / iteraciones) para mostrarlos en pantalla.
 *
 * Las velocidades de animación (INTERVALO_MS_CLASICO / _CUANTICO) están
 * pensadas para que se alcancen a ver los cambios, pero se pueden ajustar.
 */

const INTERVALO_MS_CLASICO = 260; // cada cuánto se muestra la siguiente ruta (modo clásico)
const INTERVALO_MS_CUANTICO = 500; // cada cuánto avanza una ronda de eliminación (modo cuántico)

export function useSimulacion() {
  // ---- Selección del usuario ------------------------------------------
  const [numRutas, setNumRutasState] = useState<4 | 5>(4);

  // ---- Datos traídos del backend ---------------------------------------
  const [escenario, setEscenario] = useState<EscenarioRutas | null>(null);

  // ---- Estado general de la simulación ----------------------------------
  const [modoActivo, setModoActivo] = useState<ModoSimulacion | null>(null);
  const [estado, setEstado] = useState<EstadoSimulacion>("inactivo");
  const [error, setError] = useState<string | null>(null);

  // ---- Qué se debe pintar en el mapa en este instante --------------------
  // Modo clásico: una sola ruta visible a la vez
  const [rutaVisibleClasicoId, setRutaVisibleClasicoId] = useState<number | null>(null);
  // Modo cuántico: lista de ids de rutas que siguen "vivas"
  const [rutasVisiblesCuantico, setRutasVisiblesCuantico] = useState<number[]>([]);
  // Cuando la simulación termina, aquí queda el id de la ruta ganadora
  const [rutaGanadoraId, setRutaGanadoraId] = useState<number | null>(null);

  // ---- Contador de intentos / iteraciones --------------------------------
  const [contador, setContador] = useState(0);

  // Referencia al setInterval activo, para poder cancelarlo (limpiar) cuando
  // el usuario dispara otra simulación o cuando el componente se desmonta.
  const intervaloRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const limpiarIntervalo = useCallback(() => {
    if (intervaloRef.current !== null) {
      clearInterval(intervaloRef.current);
      intervaloRef.current = null;
    }
  }, []);

  // Al desmontar el componente, se cancela cualquier temporizador que siga corriendo.
  useEffect(() => {
    return () => limpiarIntervalo();
  }, [limpiarIntervalo]);

  /** Reinicia todo lo relacionado a "qué se ve en el mapa" antes de un nuevo run. */
  const reiniciarVisualizacion = useCallback(() => {
    limpiarIntervalo();
    setRutaVisibleClasicoId(null);
    setRutasVisiblesCuantico([]);
    setRutaGanadoraId(null);
    setContador(0);
  }, [limpiarIntervalo]);

  /**
   * Trae un escenario nuevo SOLO para mostrar los puntos en el mapa (sin
   * animar ninguna ruta todavía). Se usa al cargar la página y cada vez
   * que el usuario cambia entre 4 y 5 rutas, para que el mapa nunca se vea
   * vacío/estático mientras el usuario decide qué algoritmo correr.
   */
  const cargarVistaPrevia = useCallback(async (n: 4 | 5) => {
    setError(null);
    try {
      const data = await obtenerEscenario(n);
      setEscenario(data);
    } catch (err) {
      // Si esto falla, casi siempre es porque el backend (uvicorn) no está
      // corriendo o no se puede alcanzar desde el navegador.
      console.error("No se pudo conectar con el backend:", err);
      setError(
        "No se pudo conectar con el backend en " +
          (process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000") +
          ". Verifica que 'python -m uvicorn app:app --reload --port 8000' siga corriendo en otra terminal."
      );
    }
  }, []);

  // Al montar la página por primera vez, cargamos una vista previa con el
  // número de rutas por default (4), para que el mapa aparezca con puntos
  // desde el principio en vez de quedarse vacío hasta que el usuario le dé
  // click a Clasico/Cuantico.
  useEffect(() => {
    cargarVistaPrevia(4);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /** El usuario cambia cuántos puntos de entrega quiere (4 o 5). */
  const seleccionarNumRutas = useCallback(
    (n: 4 | 5) => {
      setNumRutasState(n);
      setModoActivo(null);
      setEstado("inactivo");
      reiniciarVisualizacion();
      cargarVistaPrevia(n); // mostramos de una vez los nuevos puntos en el mapa
    },
    [reiniciarVisualizacion, cargarVistaPrevia]
  );

  /** Reproduce el guion clásico: una ruta a la vez, en orden aleatorio. */
  const animarModoClasico = useCallback(
    (data: EscenarioRutas) => {
      let indice = 0;
      setEstado("corriendo");

      intervaloRef.current = setInterval(() => {
        if (indice >= data.guion_clasico.length) {
          // Ya se probaron todas las rutas: mostramos la ganadora en verde
          limpiarIntervalo();
          setRutaVisibleClasicoId(null);
          setRutaGanadoraId(data.mejor_ruta_id);
          setEstado("finalizado");
          return;
        }

        setRutaVisibleClasicoId(data.guion_clasico[indice]);
        setContador(indice + 1);
        indice++;
      }, INTERVALO_MS_CLASICO);
    },
    [limpiarIntervalo]
  );

  /** Reproduce el guion cuántico: rondas de eliminación hasta que sobreviva 1 ruta. */
  const animarModoCuantico = useCallback(
    (data: EscenarioRutas) => {
      // Ronda inicial ("superposición"): todas las rutas visibles a la vez
      setRutasVisiblesCuantico(data.rutas.map((r) => r.id));
      setEstado("corriendo");

      let indice = 0;
      intervaloRef.current = setInterval(() => {
        if (indice >= data.guion_cuantico.length) {
          limpiarIntervalo();
          setRutasVisiblesCuantico([]);
          setRutaGanadoraId(data.mejor_ruta_id);
          setEstado("finalizado");
          return;
        }

        const ronda = data.guion_cuantico[indice];
        setRutasVisiblesCuantico(ronda.visibles);
        setContador(indice + 1);
        indice++;
      }, INTERVALO_MS_CUANTICO);
    },
    [limpiarIntervalo]
  );

  /**
   * Dispara una simulación completa: pide un escenario nuevo (puntos
   * aleatorios) al backend y arranca la animación del modo elegido.
   */
  const iniciarSimulacion = useCallback(
    async (modo: ModoSimulacion) => {
      reiniciarVisualizacion();
      setModoActivo(modo);
      setEstado("cargando");
      setError(null);

      try {
        const data = await obtenerEscenario(numRutas);
        setEscenario(data);

        if (modo === "clasico") {
          animarModoClasico(data);
        } else {
          animarModoCuantico(data);
        }
      } catch (err) {
        setEstado("inactivo");
        setError(err instanceof Error ? err.message : "Error desconocido");
      }
    },
    [numRutas, reiniciarVisualizacion, animarModoClasico, animarModoCuantico]
  );

  /**
   * Botón "Reiniciar": vuelve a correr la simulación desde cero, usando
   * SIEMPRE la última configuración que el usuario eligió (mismo numRutas,
   * mismo modo -clásico o cuántico- que se corrió por última vez), pero con
   * puntos y orden de animación completamente nuevos (aleatorios).
   *
   * Si el usuario todavía no ha corrido ningún algoritmo, simplemente
   * genera una nueva vista previa de puntos con el numRutas actual.
   */
  const reiniciar = useCallback(() => {
    if (modoActivo) {
      iniciarSimulacion(modoActivo);
    } else {
      reiniciarVisualizacion();
      cargarVistaPrevia(numRutas);
    }
  }, [modoActivo, numRutas, iniciarSimulacion, reiniciarVisualizacion, cargarVistaPrevia]);

  // Número de rutas posibles con la selección actual, aunque todavía no se
  // haya corrido ninguna simulación (para mostrarlo en el cuadro "Posibilidades").
  const posibilidades = escenario ? escenario.total_rutas : factorial(numRutas - 1);

  return {
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
  };
}
