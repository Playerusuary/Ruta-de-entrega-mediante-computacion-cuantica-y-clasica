"""Geometria compartida entre la simulacion clasica y la cuantica.

Las dos partes del proyecto tienen que medir las rutas EXACTAMENTE igual: si
cada una usa su propia formula de distancia, la comparacion final no significa
nada. Todo lo que sea "que es un punto" y "cuanto mide una ruta" vive aqui y
nadie lo duplica en su modulo.

Modelo de ciudad
----------------
La ciudad es una CUADRICULA tipo Manhattan: calles horizontales y verticales
que se cruzan en nodos de coordenadas enteras (0..GRID_SIZE). Los puntos de
entrega caen sobre esos nodos, y el vehiculo circula por las calles, nunca en
diagonal. Por eso la distancia es Manhattan (|dx| + |dy|) y no hay otra
metrica: no seria fiel al modelo permitir que el vehiculo corte en diagonal.

Ese modelo de cuadricula viene de la rama del compañero: encaja mejor con el
"mapa tipo maps" del enunciado que un canvas libre con distancia en linea recta.

Las coordenadas que se exponen son de CUADRICULA, no pixeles. El frontend las
escala al tamaño del canvas que quiera dibujar.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from itertools import permutations
from typing import Iterator, List, Optional, Sequence, Tuple

# Numero de manzanas por lado. Con 6 hay nodos en 0..6, o sea 7 calles en cada
# direccion y un tablero de 6x6 manzanas.
GRID_SIZE = 6

# Etiquetas legibles. El primer punto es siempre el deposito / base.
_ETIQUETAS = ["Base", "A", "B", "C", "D", "E", "F", "G"]

# Tolerancia para comparar distancias al detectar empates.
TOLERANCIA = 1e-9


@dataclass(frozen=True)
class Punto:
    """Un destino sobre un nodo de la cuadricula."""

    id: int
    x: float
    y: float
    etiqueta: str = ""


def distancia(a: Punto, b: Punto) -> float:
    """Distancia Manhattan: el vehiculo va por las calles, nunca en diagonal."""
    return abs(a.x - b.x) + abs(a.y - b.y)


def longitud_ruta(ruta: Sequence[Punto], cerrada: bool = False) -> float:
    """Suma de los tramos consecutivos de una ruta.

    cerrada=False (default) es el caso del enunciado: el vehiculo visita los
    puntos y se queda en el ultimo. cerrada=True agrega el tramo de regreso al
    deposito, que es el escenario del TSP clasico.
    """
    if len(ruta) < 2:
        return 0.0
    total = sum(distancia(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1))
    if cerrada:
        total += distancia(ruta[-1], ruta[0])
    return total


def rutas_posibles(puntos: Sequence[Punto]) -> Iterator[Tuple[Punto, ...]]:
    """Genera todas las rutas dejando el primer punto fijo como deposito.

    Fijar el deposito es lo que baja 5! = 120 permutaciones a 4! = 24 rutas.
    El orden que produce itertools.permutations es determinista, asi que dos
    corridas con los mismos puntos generan las rutas en la misma secuencia.

    Las dos simulaciones parten de ESTA misma lista: el modo clasico las prueba
    una por una, el cuantico las pone todas en superposicion.
    """
    if not puntos:
        return
    deposito, resto = puntos[0], tuple(puntos[1:])
    for orden in permutations(resto):
        yield (deposito,) + orden


def total_rutas(n_puntos: int) -> int:
    """Cuantas rutas hay para n puntos con el deposito fijo: (n-1)!

    Aqui se ve la explosion combinatoria que motiva todo el proyecto:
    5 puntos -> 24 rutas, 8 -> 5040, 11 -> 3628800.
    """
    return math.factorial(n_puntos - 1) if n_puntos > 1 else 1


@dataclass(frozen=True)
class RutaMedida:
    """Una ruta ya evaluada. Es la unidad que comparten ambos modos."""

    id: int
    # Ids de los puntos en orden de recorrido. Si la ruta es cerrada, el
    # deposito aparece tambien al final para que el frontend dibuje el regreso.
    orden: List[int]
    distancia: float


def medir_todas_las_rutas(
    puntos: Sequence[Punto], cerrada: bool = False
) -> List[RutaMedida]:
    """Calcula todas las rutas posibles con su distancia total.

    Es el punto de partida de los dos modos, para garantizar que evaluan
    exactamente el mismo conjunto con exactamente la misma formula.
    """
    medidas: List[RutaMedida] = []
    for i, ruta in enumerate(rutas_posibles(puntos)):
        ids = [p.id for p in ruta]
        if cerrada:
            ids = ids + [ruta[0].id]
        medidas.append(
            RutaMedida(
                id=i,
                orden=ids,
                distancia=round(longitud_ruta(ruta, cerrada=cerrada), 4),
            )
        )
    return medidas


def indices_mas_cortas(rutas: Sequence[RutaMedida]) -> List[int]:
    """Ids de las rutas de distancia minima (puede haber empate).

    Los empates son la norma, no la excepcion: en una ruta cerrada, una ruta y
    su reversa recorren las mismas calles y miden identico. Con distancia
    Manhattan sobre enteros ademas coinciden rutas que no son reversas entre si.
    Ignorar esto es lo que rompe el modo cuantico, que necesita saber cuantos
    estados marca su oraculo.
    """
    if not rutas:
        return []
    minima = min(r.distancia for r in rutas)
    return [r.id for r in rutas if math.isclose(r.distancia, minima, abs_tol=TOLERANCIA)]


def generar_puntos(
    n: int = 5,
    grid_size: int = GRID_SIZE,
    semilla: Optional[int] = None,
) -> List[Punto]:
    """Coloca n destinos sobre nodos distintos de la cuadricula.

    El punto 0 es el deposito. Las coordenadas son enteras (0..grid_size); el
    frontend las escala a pixeles.

    La semilla importa para el proyecto: pasando la misma semilla, la parte
    clasica y la cuantica corren sobre EL MISMO mapa, que es lo unico que hace
    justa la comparacion.
    """
    if n < 2:
        raise ValueError("se necesitan al menos 2 puntos")

    nodos = [(x, y) for x in range(grid_size + 1) for y in range(grid_size + 1)]
    if n > len(nodos):
        raise ValueError(
            "no caben %d puntos en una cuadricula de %dx%d" % (n, grid_size, grid_size)
        )

    rng = random.Random(semilla)
    elegidos = rng.sample(nodos, n)
    return [
        Punto(id=i, x=float(x), y=float(y), etiqueta=_etiqueta(i))
        for i, (x, y) in enumerate(elegidos)
    ]


def _etiqueta(i: int) -> str:
    return _ETIQUETAS[i] if i < len(_ETIQUETAS) else "P%d" % i
