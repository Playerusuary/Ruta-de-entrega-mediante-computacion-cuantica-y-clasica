"""Parte 1 - Simulacion clasica (bit).

Fuerza bruta deliberada: evalua las rutas UNA POR UNA, en secuencia, sin podar
ni optimizar. Un bit esta en un solo estado a la vez, y el analogo aqui es que
el simulador solo puede "mirar" una ruta a la vez.

  NO OPTIMIZAR ESTE MODULO.

Nada de vecino mas cercano, nada de programacion dinamica, nada de poda por
cota. Si el clasico se vuelve listo deja de ser el grupo de control y la
comparacion contra la parte cuantica pierde todo el sentido. Su trabajo es ser
exhaustivo y honesto, no rapido.

La simulacion devuelve la traza COMPLETA (los 24 pasos en orden) en una sola
llamada. El frontend la reproduce al ritmo que quiera: asi el servidor no
guarda estado entre frames y la velocidad de la animacion es decision del
front, no de la red.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from .geometria import Punto, longitud_ruta, rutas_posibles, total_rutas


@dataclass
class PasoClasico:
    """Una ruta evaluada. Es un frame de la animacion."""

    # Contador de rutas evaluadas, arranca en 1. Es el numero que se muestra
    # en pantalla y el que se compara contra las iteraciones del modo cuantico.
    indice: int
    # Ids de los puntos en el orden recorrido.
    ruta: List[int]
    distancia: float
    # True si esta ruta rompio el record; el front la resalta en ese frame.
    es_mejor: bool
    # Estado del "mejor hasta ahora" despues de evaluar este paso, para que el
    # front pueda dibujar la ruta campeona en paralelo sin recalcular nada.
    mejor_ruta: List[int] = field(default_factory=list)
    mejor_distancia: float = 0.0


@dataclass
class ResultadoClasico:
    puntos: List[Punto]
    cerrada: bool
    total_rutas: int
    pasos: List[PasoClasico]
    mejor_ruta: List[int]
    mejor_distancia: float
    rutas_evaluadas: int


def simular(puntos: Sequence[Punto], cerrada: bool = False) -> ResultadoClasico:
    """Recorre todas las rutas posibles y se queda con la mas corta.

    Args:
        puntos: destinos; el primero es la base y queda fijo.
        cerrada: si el dron regresa a la base al terminar.

    Returns:
        La traza completa, lista para animarse paso a paso.
    """
    if len(puntos) < 2:
        raise ValueError("se necesitan al menos 2 puntos para armar una ruta")

    puntos = list(puntos)
    pasos: List[PasoClasico] = []

    mejor_ruta: List[int] = []
    mejor_distancia = float("inf")

    for indice, ruta in enumerate(rutas_posibles(puntos), start=1):
        # Paso 1: medir esta ruta y solo esta. Un estado a la vez.
        d = longitud_ruta(ruta, cerrada=cerrada)
        ids = [p.id for p in ruta]

        # Paso 2: compararla contra el record vigente.
        es_mejor = d < mejor_distancia
        if es_mejor:
            mejor_distancia = d
            mejor_ruta = ids

        # Paso 3: registrar el frame y seguir con la siguiente.
        pasos.append(
            PasoClasico(
                indice=indice,
                ruta=ids,
                distancia=round(d, 2),
                es_mejor=es_mejor,
                mejor_ruta=list(mejor_ruta),
                mejor_distancia=round(mejor_distancia, 2),
            )
        )

    return ResultadoClasico(
        puntos=puntos,
        cerrada=cerrada,
        total_rutas=total_rutas(len(puntos)),
        pasos=pasos,
        mejor_ruta=mejor_ruta,
        mejor_distancia=round(mejor_distancia, 2),
        rutas_evaluadas=len(pasos),
    )
