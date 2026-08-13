"""Geometria compartida entre la simulacion clasica y la cuantica.

Las dos partes del proyecto tienen que medir las rutas EXACTAMENTE igual: si
cada una usa su propia formula de distancia, la comparacion final no significa
nada. Todo lo que sea "que es un punto" y "cuanto mide una ruta" vive aqui y
nadie lo duplica en su modulo.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from itertools import permutations
from typing import Iterator, List, Optional, Sequence, Tuple

# Etiquetas legibles para los puntos. El primero es siempre la base.
_ETIQUETAS = ["Base", "A", "B", "C", "D", "E", "F", "G"]


@dataclass(frozen=True)
class Punto:
    """Un destino en el canvas. Las coordenadas son pixeles."""

    id: int
    x: float
    y: float
    etiqueta: str = ""


def distancia(a: Punto, b: Punto) -> float:
    """Distancia euclidiana entre dos puntos."""
    return math.hypot(b.x - a.x, b.y - a.y)


def longitud_ruta(ruta: Sequence[Punto], cerrada: bool = False) -> float:
    """Suma de los tramos consecutivos de una ruta.

    cerrada=False (default) es el caso del enunciado: el dron visita los puntos
    y se queda en el ultimo. cerrada=True agrega el tramo de regreso a la base,
    que es el escenario opcional para comparar ambos modos.
    """
    if len(ruta) < 2:
        return 0.0
    total = sum(distancia(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1))
    if cerrada:
        total += distancia(ruta[-1], ruta[0])
    return total


def rutas_posibles(puntos: Sequence[Punto]) -> Iterator[Tuple[Punto, ...]]:
    """Genera todas las rutas dejando el primer punto fijo como base.

    Fijar la base es lo que baja 5! = 120 permutaciones a 4! = 24 rutas.
    El orden que produce itertools.permutations es determinista, asi que dos
    corridas con los mismos puntos evaluan las rutas en la misma secuencia.
    """
    if not puntos:
        return
    base, resto = puntos[0], tuple(puntos[1:])
    for orden in permutations(resto):
        yield (base,) + orden


def total_rutas(n_puntos: int) -> int:
    """Cuantas rutas hay para n puntos con la base fija: (n-1)!

    Aqui se ve la explosion combinatoria que motiva todo el proyecto:
    5 puntos -> 24 rutas, 8 -> 5040, 11 -> 3628800.
    """
    return math.factorial(n_puntos - 1) if n_puntos > 1 else 1


def generar_puntos(
    n: int = 5,
    ancho: int = 800,
    alto: int = 600,
    semilla: Optional[int] = None,
    margen: int = 60,
    separacion_minima: float = 90.0,
) -> List[Punto]:
    """Genera n puntos al azar dentro del canvas, sin encimarse.

    La semilla importa para el proyecto: pasando la misma semilla, la parte
    clasica y la cuantica corren sobre EL MISMO mapa, que es lo unico que hace
    justa la comparacion.
    """
    if n < 2:
        raise ValueError("se necesitan al menos 2 puntos")

    rng = random.Random(semilla)
    puntos: List[Punto] = []

    # Con pocos puntos y separacion holgada esto converge rapido; el tope de
    # intentos solo evita un bucle infinito si piden un canvas muy apretado.
    for i in range(n):
        for _ in range(500):
            x = rng.uniform(margen, ancho - margen)
            y = rng.uniform(margen, alto - margen)
            candidato = Punto(id=i, x=round(x, 2), y=round(y, 2), etiqueta=_etiqueta(i))
            if all(distancia(candidato, p) >= separacion_minima for p in puntos):
                puntos.append(candidato)
                break
        else:
            raise ValueError(
                "no cabe otro punto con esa separacion minima; "
                "reduce n o separacion_minima, o agranda el canvas"
            )

    return puntos


def _etiqueta(i: int) -> str:
    return _ETIQUETAS[i] if i < len(_ETIQUETAS) else f"P{i}"
