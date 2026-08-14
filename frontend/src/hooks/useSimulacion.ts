"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { factorial, obtenerEscenario } from "@/lib/api";
import type { Escenario, EstadoSimulacion, ModoSimulacion } from "@/lib/tipos";

/**
 * Toda la lógica de la pantalla.
 *
 * El backend ya resolvió las dos simulaciones y mandó las trazas completas;
 * aquí solo se reproducen con un temporizador. Ningún cálculo de rutas ni de
 * distancias vive en el frontend.
 *
 * Diferencia importante contra la versión de la rama del compañero: allá cada
 * click pedía un escenario NUEVO, así que el modo clásico y el cuántico nunca
 * corrían sobre el mismo mapa. Aquí el escenario se pide una vez y los dos
 * modos se animan sobre él — que es lo único que hace comparable el resultado.
 * Para cambiar de mapa está el botón aparte.
 */

/** Cada cuánto avanza un frame. El cuántico va más lento: son 2-3 iteraciones. */
const INTERVALO_MS_CLASICO = 240;
const INTERVALO_MS_CUANTICO = 1100;

export function useSimulacion() {
  const [n, setN] = useState<4 | 5>(5);
  const [cerrada, setCerrada] = useState(false);

  const [escenario, setEscenario] = useState<Escenario | null>(null);
  const [modoActivo, setModoActivo] = useState<ModoSimulacion | null>(null);
  const [estado, setEstado] = useState<EstadoSimulacion>("cargando");
  const [error, setError] = useState<string | null>(null);

  /** Índice del frame que se está mostrando dentro de la traza del modo activo. */
  const [indicePaso, setIndicePaso] = useState(0);
  /** Ruta ganadora, ya terminada la animación. */
  const [rutaGanadora, setRutaGanadora] = useState<number[] | null>(null);

  const intervaloRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const limpiarIntervalo = useCallback(() => {
    if (intervaloRef.current !== null) {
      clearInterval(intervaloRef.current);
      intervaloRef.current = null;
    }
  }, []);

  useEffect(() => limpiarIntervalo, [limpiarIntervalo]);

  const reiniciarVista = useCallback(() => {
    limpiarIntervalo();
    setIndicePaso(0);
    setRutaGanadora(null);
    setModoActivo(null);
  }, [limpiarIntervalo]);

  /** Pide un escenario nuevo y deja el mapa listo, sin animar nada todavía. */
  const cargarEscenario = useCallback(
    async (opciones: { n: 4 | 5; cerrada: boolean }) => {
      reiniciarVista();
      setEstado("cargando");
      setError(null);
      try {
        const data = await obtenerEscenario(opciones);
        setEscenario(data);
        setEstado("inactivo");
      } catch (err) {
        setEscenario(null);
        setEstado("inactivo");
        setError(err instanceof Error ? err.message : "Error desconocido");
      }
    },
    [reiniciarVista],
  );

  // Mapa inicial al abrir la página.
  useEffect(() => {
    cargarEscenario({ n: 5, cerrada: false });
  }, [cargarEscenario]);

  /** Reproduce la traza del modo elegido sobre el escenario ya cargado. */
  const iniciar = useCallback(
    (modo: ModoSimulacion) => {
      if (!escenario) return;
      limpiarIntervalo();
      setModoActivo(modo);
      setRutaGanadora(null);
      setIndicePaso(0);
      setEstado("corriendo");

      const traza =
        modo === "clasico" ? escenario.clasico.pasos : escenario.cuantico.pasos;
      const intervalo =
        modo === "clasico" ? INTERVALO_MS_CLASICO : INTERVALO_MS_CUANTICO;

      let i = 0;
      intervaloRef.current = setInterval(() => {
        i++;
        if (i >= traza.length) {
          limpiarIntervalo();
          setIndicePaso(traza.length - 1);
          setRutaGanadora(
            modo === "clasico"
              ? escenario.clasico.mejor_ruta
              : escenario.cuantico.medicion_ruta,
          );
          setEstado("finalizado");
          return;
        }
        setIndicePaso(i);
      }, intervalo);
    },
    [escenario, limpiarIntervalo],
  );

  const nuevoMapa = useCallback(() => {
    cargarEscenario({ n, cerrada });
  }, [cargarEscenario, n, cerrada]);

  const cambiarN = useCallback(
    (valor: 4 | 5) => {
      setN(valor);
      cargarEscenario({ n: valor, cerrada });
    },
    [cargarEscenario, cerrada],
  );

  const cambiarCerrada = useCallback(
    (valor: boolean) => {
      setCerrada(valor);
      cargarEscenario({ n, cerrada: valor });
    },
    [cargarEscenario, n],
  );

  /** Vuelve a animar el mismo modo sobre el mismo mapa. */
  const repetir = useCallback(() => {
    if (modoActivo) iniciar(modoActivo);
  }, [modoActivo, iniciar]);

  // ---- Lo que el mapa necesita pintar en este frame ----------------------

  const pasoClasico =
    modoActivo === "clasico" && escenario
      ? escenario.clasico.pasos[indicePaso]
      : null;

  const pasoCuantico =
    modoActivo === "cuantico" && escenario
      ? escenario.cuantico.pasos[indicePaso]
      : null;

  const corriendo = estado === "corriendo" || estado === "cargando";

  const totalFrames = escenario
    ? modoActivo === "clasico"
      ? escenario.clasico.pasos.length
      : modoActivo === "cuantico"
        ? escenario.cuantico.pasos.length - 1 // el paso 0 es la superposición
        : 0
    : 0;

  const contador =
    modoActivo === "clasico"
      ? (pasoClasico?.indice ?? 0)
      : (pasoCuantico?.indice ?? 0);

  // Lo que el mapa debe pintar en este frame.
  //
  // Al terminar la búsqueda se descartan TODAS las rutas y solo sobrevive la
  // ganadora: el mapa queda limpio con la respuesta, sin la maraña de las
  // candidatas perdedoras encima. Mientras corre sí se ven, porque ver a la
  // simulación descartarlas es justamente lo que se está mostrando.
  const finalizado = estado === "finalizado";

  return {
    // configuración
    n,
    cerrada,
    cambiarN,
    cambiarCerrada,
    // datos
    escenario,
    error,
    estado,
    modoActivo,
    corriendo,
    // acciones
    iniciar,
    nuevoMapa,
    repetir,
    // frame actual (para la barra de estado)
    pasoClasico,
    pasoCuantico,
    rutaGanadora,
    contador,
    totalFrames,
    // lo que dibuja el mapa: al finalizar solo queda la ganadora
    rutaClasicaId: finalizado ? null : (pasoClasico?.ruta_id ?? null),
    mejorParcial: finalizado ? null : (pasoClasico?.mejor_ruta ?? null),
    probabilidades: finalizado ? null : (pasoCuantico?.probabilidades ?? null),
    posibilidades: escenario?.clasico.total_rutas ?? factorial(n - 1),
  };
}
