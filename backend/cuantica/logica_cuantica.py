"""
============================================================================
 CUANTICA - Lógica del modo de computación cuántica (simulado)
============================================================================
Modo CUÁNTICO (simulado, NO es computación cuántica real):

Ronda 0: todas las rutas están visibles ("en superposición"), cada una
          con probabilidad inicial = 1 / total_rutas.

En cada ronda siguiente, el "Mecanismo A" elimina (desvanece) un grupo de
las rutas que peor distancia tienen entre las que aún quedan visibles.
Esto sube relativamente la probabilidad de las rutas buenas (menor
distancia) y hace desaparecer las malas, hasta que solo queda 1: la mejor
ruta posible.

Como el ejercicio pide que la simulación cuántica "se vea" mucho más
rápida que la clásica, aquí NO se elimina un porcentaje fijo por ronda
(lo cual podría tardar muchas rondas si hay muchas rutas): en vez de eso
se decide DE ANTEMANO cuántas rondas va a durar la animación -un número
aleatorio entre MIN_RONDAS_CUANTICO y MAX_RONDAS_CUANTICO (4 a 8)- y se
reparten las eliminaciones necesarias entre esas rondas. Así el modo
cuántico siempre "termina rápido", sin importar si hay 6 o 24 rutas en
total.

Usa las rutas ya calculadas en backend/comun/geometria.py
(calcular_todas_las_rutas) - aquí solo se decide en qué RONDAS se van
eliminando esas rutas.

Usado por: backend/app.py
============================================================================
"""

import math
import random

# Límites para cuántas "rondas" (iteraciones) se le permiten al modo
# cuántico simulado. La idea es que, sin importar cuántas rutas totales
# haya (6 para 4 puntos, 24 para 5 puntos), el modo cuántico SIEMPRE
# converja en muy pocos pasos -para simular que es mucho más rápido que
# el modo clásico, que sí prueba las rutas una por una-.
MIN_RONDAS_CUANTICO = 4
MAX_RONDAS_CUANTICO = 8


def construir_guion_cuantico(rutas: list[dict], mejor_ruta_id: int) -> list[dict]:
    """
    Construye el guion de rondas de eliminación del modo cuántico simulado.

    IMPORTANTE (nota de depuración): en este problema es MUY común que
    dos rutas distintas tengan exactamente la misma distancia (por
    ejemplo, una ruta y su recorrido "en reversa" pasan por las mismas
    calles y miden igual). Si eso pasa justo entre las últimas rutas que
    quedan, un empate podría hacer que se elimine por error a la ruta
    que el backend ya declaró oficialmente como "mejor_ruta_id".
    Para evitar esa inconsistencia visual, la ruta ganadora (mejor_ruta_id)
    NUNCA se incluye entre las candidatas a eliminar; siempre sobrevive
    hasta el final, aunque otras rutas tengan su misma distancia.

    Devuelve una lista de "rondas". Cada ronda es un diccionario con:
        - ronda: número de ronda (0, 1, 2, ...)
        - visibles: ids de rutas que siguen visibles DESPUÉS de esta ronda
        - eliminadas_en_esta_ronda: ids de rutas que se acaban de desvanecer
    """
    ids_restantes = [r["id"] for r in rutas]
    distancia_por_id = {r["id"]: r["distancia"] for r in rutas}

    total_a_eliminar_al_final = len(ids_restantes) - 1
    if total_a_eliminar_al_final <= 0:
        return []

    # Elegimos cuántas rondas va a durar la animación (acotado a 8 o menos,
    # y nunca más rondas que rutas a eliminar).
    tope_rondas = min(MAX_RONDAS_CUANTICO, total_a_eliminar_al_final)
    piso_rondas = min(MIN_RONDAS_CUANTICO, tope_rondas)
    num_rondas = random.randint(piso_rondas, tope_rondas)

    rondas = []
    for numero_ronda in range(num_rondas):
        # Candidatas a eliminar = todas las que quedan MENOS la ganadora oficial
        candidatas = [rid for rid in ids_restantes if rid != mejor_ruta_id]
        # Ordenamos las candidatas de PEOR a MEJOR distancia
        candidatas.sort(key=lambda rid: distancia_por_id[rid], reverse=True)

        # Repartimos lo que falta por eliminar entre las rondas que quedan,
        # para llegar exactamente a 1 ruta viva cuando se acaben las rondas.
        rondas_restantes = num_rondas - numero_ronda
        faltan_por_eliminar = len(ids_restantes) - 1
        cantidad_a_eliminar = math.ceil(faltan_por_eliminar / rondas_restantes)
        cantidad_a_eliminar = max(1, min(cantidad_a_eliminar, len(candidatas)))

        eliminadas = candidatas[:cantidad_a_eliminar]
        ids_restantes = [rid for rid in ids_restantes if rid not in eliminadas]

        rondas.append({
            "ronda": numero_ronda,
            "eliminadas_en_esta_ronda": eliminadas,
            "visibles": list(ids_restantes),
        })

    return rondas
