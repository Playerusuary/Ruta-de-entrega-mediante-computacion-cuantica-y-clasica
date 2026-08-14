"""Parte 2 - Simulacion cuantica (qubit): amplificacion de probabilidad.

Es una SIMULACION de amplificacion de amplitud (Grover) sobre rutas, corriendo
en una computadora clasica. No hay hardware cuantico ni librerias cuanticas.

Como funciona
-------------
Cada una de las N rutas es un estado. Se arranca en superposicion uniforme:
todas con amplitud 1/sqrt(N), o sea probabilidad 1/N -exactamente la
"probabilidad inicial igual" que pide el enunciado-.

Cada iteracion aplica el Mecanismo A en dos tiempos:

  1. Oraculo: invierte el signo de la amplitud de las rutas que cumplen la
     condicion (distancia minima).
  2. Difusion: refleja todas las amplitudes alrededor de su promedio
     ("inversion sobre la media").

El efecto neto es que la amplitud de las rutas marcadas sube y la del resto
baja. La probabilidad es la amplitud al cuadrado, y es lo que el frontend usa
como opacidad: las rutas malas se desvanecen solas, sin que nadie las borre
a mano.

Numero de iteraciones
---------------------
No es arbitrario ni aleatorio: es el optimo de Grover,

    k = floor( (pi/4) * sqrt(N/M) )

con N rutas y M rutas marcadas. Para 24 rutas con una sola ganadora da k = 3,
y la probabilidad de medir la correcta queda en ~98%. Pasarse de k EMPEORA el
resultado (la amplitud vuelve a bajar), y esa es justamente la propiedad
interesante que conviene enseñar en la presentacion.

Que cambio respecto a la version de la rama del compañero
---------------------------------------------------------
Su version funcionaba y estaba honestamente documentada, pero tenia dos cosas
que conviene revisar (esto es de su parte, asi que la ultima palabra es suya):

  1. Recibia `mejor_ruta_id` ya calculado y lo protegia de la eliminacion. Con
     eso la simulacion no encontraba la mejor ruta: se le entregaba y ella
     coreografiaba el desvanecimiento alrededor. Aqui la ganadora sale de las
     probabilidades, no se inyecta.
  2. El numero de rondas era random.randint(4, 8), elegido para "verse rapido".
     Aqui se deriva de N y M con la formula de Grover.

Sobre la circularidad del oraculo: si, para SIMULAR el oraculo hay que saber
cuales rutas son minimas. Eso es inherente a simular Grover en una maquina
clasica y no es trampa -en el modelo, el oraculo es una caja negra que
reconoce una solucion sin que el buscador sepa cual es-. Lo que se cuenta y se
compara contra el modo clasico son las CONSULTAS AL ORACULO (las iteraciones),
que es justo la medida donde Grover afirma su ventaja: ~sqrt(N) contra N.

Se conserva de su version la idea de reportar por ronda que rutas siguen
"visibles" y cuales se acaban de desvanecer, para que su frontend siga
sirviendo sin cambios conceptuales.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from .geometria import (
    Punto,
    RutaMedida,
    indices_mas_cortas,
    medir_todas_las_rutas,
    total_rutas,
)

# Una ruta se considera "visible" mientras su probabilidad no caiga por debajo
# de la mitad de la probabilidad inicial uniforme (1/N). Es solo una ayuda de
# presentacion: la opacidad real deberia salir de `probabilidad`.
FACTOR_UMBRAL_VISIBLE = 0.5


@dataclass
class ProbabilidadRuta:
    ruta_id: int
    distancia: float
    probabilidad: float


@dataclass
class PasoCuantico:
    """Una iteracion. Es un frame de la animacion."""

    # 0 = superposicion inicial (antes de amplificar), luego 1, 2, 3...
    indice: int
    # Probabilidad de TODAS las rutas en este instante: todas siguen existiendo,
    # eso es la superposicion. El frontend las dibuja todas a la vez.
    probabilidades: List[ProbabilidadRuta]
    # Vista derivada, para conservar el concepto de la rama del compañero.
    visibles: List[int] = field(default_factory=list)
    eliminadas_en_esta_ronda: List[int] = field(default_factory=list)
    # Probabilidad acumulada de las rutas marcadas: la "confianza" del sistema.
    probabilidad_marcadas: float = 0.0


@dataclass
class ResultadoCuantico:
    puntos: List[Punto]
    rutas: List[RutaMedida]
    cerrada: bool
    total_rutas: int
    pasos: List[PasoCuantico]
    # Iteraciones de Grover ejecutadas (sin contar el paso 0). Es el numero que
    # se compara contra las rutas evaluadas del modo clasico.
    iteraciones: int
    # Rutas que el oraculo marca (distancia minima). Puede haber empate.
    rutas_marcadas: List[int]
    # Resultado de medir al final con la funcion ponderada.
    medicion_id: int
    medicion_ruta: List[int]
    medicion_distancia: float
    # True si la medicion cayo en una ruta marcada. Casi siempre lo es, pero
    # NO siempre: el modo cuantico es probabilistico y puede fallar. Enseñar
    # ese fallo ocasional vale mas que esconderlo.
    acerto: bool
    probabilidad_final_marcadas: float


def iteraciones_optimas(n_rutas: int, n_marcadas: int) -> int:
    """Numero optimo de iteraciones de Grover: floor((pi/4) * sqrt(N/M))."""
    if n_rutas <= 0 or n_marcadas <= 0 or n_marcadas >= n_rutas:
        return 0
    return max(1, math.floor((math.pi / 4) * math.sqrt(n_rutas / n_marcadas)))


def simular(
    puntos: Sequence[Punto],
    cerrada: bool = False,
    semilla: Optional[int] = None,
    iteraciones: Optional[int] = None,
) -> ResultadoCuantico:
    """Corre la amplificacion de probabilidad y devuelve la traza completa.

    Args:
        puntos: destinos; el primero es el deposito y queda fijo.
        cerrada: si el vehiculo regresa al deposito.
        semilla: hace reproducible la medicion final ponderada.
        iteraciones: forzar un numero de iteraciones. Sirve para demostrar que
            pasarse del optimo EMPEORA el resultado. None = usar el optimo.

    Returns:
        La traza completa: una entrada por iteracion, con la probabilidad de
        todas las rutas en cada una.
    """
    if len(puntos) < 2:
        raise ValueError("se necesitan al menos 2 puntos para armar una ruta")

    puntos = list(puntos)
    rutas = medir_todas_las_rutas(puntos, cerrada=cerrada)
    n = len(rutas)
    marcadas = indices_mas_cortas(rutas)
    es_marcada = [r.id in set(marcadas) for r in rutas]

    k = iteraciones_optimas(n, len(marcadas)) if iteraciones is None else max(0, iteraciones)

    # Superposicion inicial: todas las rutas con la misma amplitud.
    amplitudes = [1.0 / math.sqrt(n)] * n
    umbral = (1.0 / n) * FACTOR_UMBRAL_VISIBLE

    pasos: List[PasoCuantico] = []
    visibles_previas = [r.id for r in rutas]
    pasos.append(_armar_paso(0, rutas, amplitudes, es_marcada, umbral, visibles_previas))
    visibles_previas = list(pasos[0].visibles)

    for paso in range(1, k + 1):
        # 1. Oraculo: marca las rutas que cumplen la condicion invirtiendo su signo.
        for i in range(n):
            if es_marcada[i]:
                amplitudes[i] = -amplitudes[i]

        # 2. Difusion: inversion sobre la media. Lo que estaba por debajo del
        #    promedio baja y lo que estaba por encima sube.
        media = sum(amplitudes) / n
        amplitudes = [2 * media - a for a in amplitudes]

        frame = _armar_paso(paso, rutas, amplitudes, es_marcada, umbral, visibles_previas)
        pasos.append(frame)
        visibles_previas = list(frame.visibles)

    # Medicion final ponderada por probabilidad. No se elige el maximo a mano:
    # se muestrea, que es lo que hace una medicion real.
    probabilidades = [a * a for a in amplitudes]
    rng = random.Random(semilla)
    medida = _muestrear(rng, probabilidades)
    ruta_medida = rutas[medida]

    return ResultadoCuantico(
        puntos=puntos,
        rutas=rutas,
        cerrada=cerrada,
        total_rutas=total_rutas(len(puntos)),
        pasos=pasos,
        iteraciones=k,
        rutas_marcadas=marcadas,
        medicion_id=ruta_medida.id,
        medicion_ruta=list(ruta_medida.orden),
        medicion_distancia=ruta_medida.distancia,
        acerto=ruta_medida.id in set(marcadas),
        probabilidad_final_marcadas=round(
            sum(p for i, p in enumerate(probabilidades) if es_marcada[i]), 6
        ),
    )


def _armar_paso(
    indice: int,
    rutas: Sequence[RutaMedida],
    amplitudes: Sequence[float],
    es_marcada: Sequence[bool],
    umbral: float,
    visibles_previas: Sequence[int],
) -> PasoCuantico:
    probabilidades = [a * a for a in amplitudes]

    detalle = [
        ProbabilidadRuta(
            ruta_id=ruta.id,
            distancia=ruta.distancia,
            probabilidad=round(probabilidades[i], 6),
        )
        for i, ruta in enumerate(rutas)
    ]

    visibles = [ruta.id for i, ruta in enumerate(rutas) if probabilidades[i] >= umbral]
    previas = set(visibles_previas)
    eliminadas = sorted(previas - set(visibles))

    return PasoCuantico(
        indice=indice,
        probabilidades=detalle,
        visibles=visibles,
        eliminadas_en_esta_ronda=eliminadas,
        probabilidad_marcadas=round(
            sum(p for i, p in enumerate(probabilidades) if es_marcada[i]), 6
        ),
    )


def _muestrear(rng: random.Random, probabilidades: Sequence[float]) -> int:
    """Elige un indice al azar ponderado por probabilidad."""
    total = sum(probabilidades)
    objetivo = rng.random() * total
    acumulado = 0.0
    for i, p in enumerate(probabilidades):
        acumulado += p
        if objetivo <= acumulado:
            return i
    return len(probabilidades) - 1
