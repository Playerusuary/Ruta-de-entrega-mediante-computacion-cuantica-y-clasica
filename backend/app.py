"""
============================================================================
 BACKEND - Simulación de rutas de entrega (Clásico vs "Cuántico")
============================================================================

Qué hace este archivo:

Este archivo YA NO contiene la lógica de cálculo: solo ORQUESTA. Expone el
endpoint HTTP, arma la app de FastAPI, y llama a las funciones que viven en:

    - comun/geometria.py         -> puntos, distancias, todas las rutas
    - clasico/logica_clasica.py  -> guion del modo clásico
    - cuantica/logica_cuantica.py -> guion del modo cuántico (simulado)

1. Define una ciudad en forma de CUADRÍCULA (como Manhattan): calles
   horizontales y verticales que se cruzan en "nodos". Los edificios van
   en los espacios entre calles. (comun/geometria.py)

2. Genera N puntos de entrega (4 o 5) colocados en nodos aleatorios de
   esa cuadrícula. El punto de partida (el "depósito") siempre es el
   primer punto generado y se queda FIJO al calcular las rutas (por eso
   para 5 puntos hay 4! = 24 rutas, y para 4 puntos hay 3! = 6 rutas:
   solo permutamos los puntos que NO son el origen). (comun/geometria.py)

3. Calcula TODAS las rutas posibles (permutaciones) y su distancia total,
   usando distancia "Manhattan" (|dx| + |dy|) porque el auto solo puede
   moverse por las calles de la cuadrícula, nunca en diagonal.
   (comun/geometria.py)

4. Como el ejercicio pide ver la simulación "en vivo" pero SIN usar
   librerías cuánticas reales (es una analogía visual, no computación
   cuántica real), aquí no la mostramos en vivo desde el backend: en vez
   de eso, precalculamos un "guion" (schedule) con el orden exacto en el
   que se debe animar cada modo, y se lo mandamos completo al frontend.
   El frontend simplemente reproduce ese guion con temporizadores
   (setInterval), lo cual VISUALMENTE se ve en vivo, pero es mucho más
   simple y no requiere mantener una conexión abierta (WebSocket).

   - Modo CLÁSICO: el guion es un orden aleatorio de las rutas (se
     "prueban" una por una, como fuerza bruta). (clasico/logica_clasica.py)

   - Modo CUÁNTICO: el guion es una lista de "rondas" (entre 4 y 8,
     elegidas al azar), donde en cada ronda se elimina un grupo de las
     rutas peores hasta que solo sobrevive la mejor. (cuantica/logica_cuantica.py)

5. Expone un único endpoint HTTP: GET /api/rutas?n=4  (o n=5)
   que devuelve todo lo anterior en JSON.

Cómo correrlo:
    pip install -r requirements.txt
    uvicorn app:app --reload --port 8000

El backend corre en su propio puerto (8000), separado del frontend
Next.js (3000), tal como se pidió en las instrucciones.
============================================================================
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from comun.geometria import GRID_SIZE, generar_puntos, calcular_todas_las_rutas
from clasico.logica_clasica import construir_guion_clasico
from cuantica.logica_cuantica import construir_guion_cuantico

app = FastAPI(title="TSP Dron/Auto - Clásico vs Cuántico (simulado)")

# Habilitamos CORS para que el frontend (Next.js en otro puerto) pueda
# llamar a este backend sin que el navegador lo bloquee.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en un proyecto real se restringiría al dominio del frontend
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# Endpoint principal
# ----------------------------------------------------------------------

@app.get("/api/rutas")
def obtener_rutas(n: int = Query(4, ge=4, le=5)):
    """
    Genera un nuevo escenario aleatorio con n puntos de entrega (4 o 5)
    y devuelve TODO lo necesario para que el frontend anime ambos modos:

    {
      "grid_size": 6,
      "puntos": [ {id, x, y}, ... ],
      "rutas": [ {id, orden: [ids de puntos], distancia}, ... ],
      "mejor_ruta_id": <id de la ruta más corta>,
      "guion_clasico": [ ids de ruta en orden de animación ],
      "guion_cuantico": [ {ronda, eliminadas_en_esta_ronda, visibles}, ... ],
      "total_rutas": <número total de rutas evaluadas>
    }
    """
    puntos = generar_puntos(n)
    rutas = calcular_todas_las_rutas(puntos)

    mejor_ruta = min(rutas, key=lambda r: r["distancia"])

    guion_clasico = construir_guion_clasico(rutas)
    guion_cuantico = construir_guion_cuantico(rutas, mejor_ruta["id"])

    return {
        "grid_size": GRID_SIZE,
        "puntos": puntos,
        "rutas": rutas,
        "mejor_ruta_id": mejor_ruta["id"],
        "guion_clasico": guion_clasico,
        "guion_cuantico": guion_cuantico,
        "total_rutas": len(rutas),
    }


@app.get("/")
def raiz():
    """Endpoint de salud, solo para confirmar que el backend está vivo."""
    return {"status": "ok", "mensaje": "Backend TSP corriendo correctamente"}


# ----------------------------------------------------------------------
# Forma alternativa de arrancar el servidor: "python app.py"
# ----------------------------------------------------------------------
# Normalmente este backend se levanta con el comando:
#     python -m uvicorn app:app --reload --port 8000
# Pero en Windows a veces ese comando no se reconoce por temas de PATH.
# Como respaldo, este bloque permite simplemente correr:
#     python app.py
# host="0.0.0.0" hace que el servidor acepte conexiones tanto en
# 127.0.0.1 como en localhost, evitando problemas de resolución de
# direcciones (IPv4 vs IPv6) que causan errores de conexión en Windows.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
