"""
============================================================================
 CLASICO - Lógica del modo de computación clásica (fuerza bruta)
============================================================================
Modo CLÁSICO: el guion es un orden aleatorio de las rutas (se "prueban"
una por una, como fuerza bruta), sin ningún criterio para saltarse
ninguna ni para adivinar cuál es mejor de antemano.

Usa las rutas ya calculadas en backend/comun/geometria.py
(calcular_todas_las_rutas) - aquí solo se decide en qué ORDEN se van a
mostrar esas rutas al usuario.

Usado por: backend/app.py
============================================================================
"""

import random


def construir_guion_clasico(rutas: list[dict]) -> list[int]:
    """
    Modo clásico: el "guion" es simplemente el orden en el que se van a
    ir mostrando las rutas, UNA A LA VEZ, de forma aleatoria (como fuerza
    bruta probando soluciones sin ningún orden inteligente).

    Devuelve una lista de ids de ruta en el orden en que deben animarse.
    """
    orden_ids = [r["id"] for r in rutas]
    random.shuffle(orden_ids)
    return orden_ids
