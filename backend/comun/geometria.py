"""
============================================================================
 COMUN - Geometría de la ciudad y cálculo de rutas
============================================================================
Este archivo NO es clásico ni cuántico: es la base que ambos modos usan.

Contiene:
1. La configuración de la cuadrícula (ciudad tipo Manhattan).
2. La generación aleatoria de los puntos de entrega.
3. El cálculo de la distancia entre dos puntos (distancia Manhattan).
4. El cálculo de TODAS las rutas posibles (permutaciones) y su distancia
   total. Tanto el modo clásico como el cuántico parten de esta misma
   lista de rutas: el clásico las va probando una por una, el cuántico
   las va "eliminando" por rondas.

Usado por:
    - backend/clasico/logica_clasica.py
    - backend/cuantica/logica_cuantica.py
    - backend/app.py
============================================================================
"""

from itertools import permutations
import random

# GRID_SIZE = número de manzanas (bloques) por lado.
# Con GRID_SIZE = 6 tenemos nodos/intersecciones en 0..6 (7 líneas de
# calle en cada dirección), formando un tablero de 6x6 manzanas con
# edificio en cada una.
GRID_SIZE = 6


def generar_puntos(n: int) -> list[dict]:
    """
    Genera n coordenadas distintas dentro de la cuadrícula (nodos con
    coordenadas enteras entre 0 y GRID_SIZE).

    El punto en el índice 0 es el "depósito" / punto de partida.
    """
    nodos_posibles = [
        (x, y)
        for x in range(0, GRID_SIZE + 1)
        for y in range(0, GRID_SIZE + 1)
    ]
    elegidos = random.sample(nodos_posibles, n)
    return [{"id": i, "x": p[0], "y": p[1]} for i, p in enumerate(elegidos)]


def distancia_manhattan(a: dict, b: dict) -> int:
    """Distancia entre dos puntos siguiendo las calles (no en diagonal)."""
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


def calcular_todas_las_rutas(puntos: list[dict]) -> list[dict]:
    """
    Calcula todas las permutaciones posibles fijando puntos[0] como
    origen y destino final (la ruta es un ciclo: depósito -> entregas -> depósito).

    Devuelve una lista de rutas, cada una con:
        - id: índice de la ruta
        - orden: lista de ids de puntos en el orden que se visitan
                 (empieza y termina en el depósito)
        - distancia: distancia total del recorrido
    """
    origen = puntos[0]
    resto = puntos[1:]

    rutas = []
    for i, perm in enumerate(permutations(resto)):
        secuencia = [origen] + list(perm) + [origen]
        dist_total = sum(
            distancia_manhattan(secuencia[j], secuencia[j + 1])
            for j in range(len(secuencia) - 1)
        )
        rutas.append({
            "id": i,
            "orden": [p["id"] for p in secuencia],
            "distancia": dist_total,
        })
    return rutas
