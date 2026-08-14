"""Parte 1 - Simulacion clasica (bit).

Fuerza bruta deliberada: evalua las rutas UNA POR UNA, en secuencia, sin podar
ni optimizar. Un bit esta en un solo estado a la vez, y el analogo aqui es que
el simulador solo puede "mirar" una ruta a la vez.

  NO OPTIMIZAR ESTE MODULO.

Nada de vecino mas cercano, nada de programacion dinamica, nada de poda por
cota. Si el clasico se vuelve listo deja de ser el grupo de control y la
comparacion contra la parte cuantica pierde todo el sentido. Su trabajo es ser
exhaustivo y honesto, no rapido.

Orden de evaluacion
-------------------
Por defecto las rutas se prueban en el orden deterministico de las
permutaciones (SECUENCIAL). La rama del compañero las barajaba al azar, que es
igual de valido como "fuerza bruta sin criterio"; esa variante quedo disponible
como orden=ALEATORIO.

Se dejo SECUENCIAL como default por una razon visual: con un orden fijo, el
"mejor hasta ahora" se rompe unas pocas veces y se ve la narrativa del record
cayendo. Barajando, el record salta de forma erratica y cuesta mas leerlo.

La simulacion devuelve la traza COMPLETA en una sola llamada. El frontend la
reproduce al ritmo que quiera: asi el servidor no guarda estado entre frames y
la velocidad de la animacion es decision del front, no de la red.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence

from .geometria import (
    Punto,
    RutaMedida,
    indices_mas_cortas,
    medir_todas_las_rutas,
    total_rutas,
)


class OrdenEvaluacion(str, Enum):
    """En que orden se prueban las rutas."""

    # Orden deterministico de las permutaciones (default).
    SECUENCIAL = "secuencial"
    # Barajado, como en la rama del compañero.
    ALEATORIO = "aleatorio"


@dataclass
class PasoClasico:
    """Una ruta evaluada. Es un frame de la animacion."""

    # Contador de rutas evaluadas, arranca en 1. Es el numero que se muestra en
    # pantalla y el que se compara contra las iteraciones del modo cuantico.
    indice: int
    # Id de la ruta dentro del catalogo compartido (el mismo que usa el cuantico).
    ruta_id: int
    # Ids de los puntos en el orden recorrido.
    ruta: List[int]
    distancia: float
    # True si esta ruta rompio el record; el front la resalta en ese frame.
    es_mejor: bool
    # Estado del "mejor hasta ahora" despues de este paso, para que el front
    # pueda dibujar la ruta campeona en paralelo sin recalcular nada.
    mejor_ruta: List[int] = field(default_factory=list)
    mejor_distancia: float = 0.0


@dataclass
class ResultadoClasico:
    puntos: List[Punto]
    rutas: List[RutaMedida]
    cerrada: bool
    orden: OrdenEvaluacion
    total_rutas: int
    pasos: List[PasoClasico]
    mejor_ruta_id: int
    mejor_ruta: List[int]
    mejor_distancia: float
    rutas_evaluadas: int
    # Ids de todas las rutas que empatan en la distancia minima. Con distancia
    # Manhattan los empates son frecuentes y conviene que el front lo sepa.
    empates_en_la_mejor: List[int]


def simular(
    puntos: Sequence[Punto],
    cerrada: bool = False,
    orden: OrdenEvaluacion = OrdenEvaluacion.SECUENCIAL,
    semilla: Optional[int] = None,
) -> ResultadoClasico:
    """Recorre todas las rutas posibles y se queda con la mas corta.

    Args:
        puntos: destinos; el primero es el deposito y queda fijo.
        cerrada: si el vehiculo regresa al deposito al terminar.
        orden: en que secuencia se prueban las rutas.
        semilla: solo se usa con orden=ALEATORIO, para que el barajado
            sea reproducible.

    Returns:
        La traza completa, lista para animarse paso a paso.
    """
    if len(puntos) < 2:
        raise ValueError("se necesitan al menos 2 puntos para armar una ruta")

    puntos = list(puntos)
    rutas = medir_todas_las_rutas(puntos, cerrada=cerrada)

    secuencia = list(rutas)
    if orden == OrdenEvaluacion.ALEATORIO:
        random.Random(semilla).shuffle(secuencia)

    pasos: List[PasoClasico] = []
    mejor_ruta_id = -1
    mejor_ruta: List[int] = []
    mejor_distancia = float("inf")

    for indice, ruta in enumerate(secuencia, start=1):
        # Paso 1: mirar esta ruta y solo esta. Un estado a la vez.
        # Paso 2: compararla contra el record vigente.
        es_mejor = ruta.distancia < mejor_distancia
        if es_mejor:
            mejor_ruta_id = ruta.id
            mejor_ruta = list(ruta.orden)
            mejor_distancia = ruta.distancia

        # Paso 3: registrar el frame y seguir con la siguiente.
        pasos.append(
            PasoClasico(
                indice=indice,
                ruta_id=ruta.id,
                ruta=list(ruta.orden),
                distancia=ruta.distancia,
                es_mejor=es_mejor,
                mejor_ruta=list(mejor_ruta),
                mejor_distancia=mejor_distancia,
            )
        )

    return ResultadoClasico(
        puntos=puntos,
        rutas=rutas,
        cerrada=cerrada,
        orden=orden,
        total_rutas=total_rutas(len(puntos)),
        pasos=pasos,
        mejor_ruta_id=mejor_ruta_id,
        mejor_ruta=mejor_ruta,
        mejor_distancia=mejor_distancia,
        rutas_evaluadas=len(pasos),
        empates_en_la_mejor=indices_mas_cortas(rutas),
    )
