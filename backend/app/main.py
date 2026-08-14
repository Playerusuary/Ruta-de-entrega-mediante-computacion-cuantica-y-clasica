"""API del simulador de ruta de entrega.

El backend hace la logica (permutaciones, distancias, amplificacion) y el
frontend solo dibuja. Cada endpoint responde en una sola llamada con todo lo
que el canvas necesita para animar, sin estado de sesion en el servidor.

Endpoints
---------
GET  /health                    salud
GET  /api/v1/puntos             genera el mapa
POST /api/v1/clasico/simular    traza del modo clasico
POST /api/v1/cuantico/simular   traza del modo cuantico
GET  /api/v1/escenario          mapa + los dos modos en una sola llamada

El ultimo es el que conviene usar desde el frontend: garantiza por
construccion que ambos modos corren sobre el mismo mapa.
La idea de resolver todo en una llamada viene de la rama del compañero.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import clasico, cuantico
from .clasico import OrdenEvaluacion
from .esquemas import (
    EscenarioResponse,
    PuntosResponse,
    SimulacionClasicaRequest,
    SimulacionClasicaResponse,
    SimulacionCuanticaRequest,
    SimulacionCuanticaResponse,
)
from .geometria import GRID_SIZE, Punto, generar_puntos

app = FastAPI(
    title="Ruta de entrega - cuantica vs clasica",
    description=(
        "Simulador de mini TSP (4-5 puntos) sobre una ciudad en cuadricula, "
        "resuelto por fuerza bruta clasica y por amplificacion de probabilidad."
    ),
    version="0.2.0",
)

# El front de Next.js corre en :3000 en desarrollo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/v1/puntos", response_model=PuntosResponse)
def puntos(
    n: int = Query(5, ge=2, le=8, description="Cuantos destinos generar."),
    grid_size: int = Query(GRID_SIZE, ge=2, le=20, description="Manzanas por lado."),
    semilla: Optional[int] = Query(
        None,
        description=(
            "Fija el mapa. Con la misma semilla, el modo clasico y el cuantico "
            "corren sobre exactamente los mismos puntos."
        ),
    ),
) -> PuntosResponse:
    """Genera un mapa de destinos sobre nodos de la cuadricula."""
    generados = _generar(n=n, grid_size=grid_size, semilla=semilla)
    return PuntosResponse(
        puntos=[p.__dict__ for p in generados],
        grid_size=grid_size,
        semilla=semilla,
    )


@app.post("/api/v1/clasico/simular", response_model=SimulacionClasicaResponse)
def simular_clasico(payload: SimulacionClasicaRequest) -> SimulacionClasicaResponse:
    """Corre la simulacion clasica y devuelve la traza completa.

    La respuesta trae los (n-1)! pasos en orden de evaluacion. El frontend los
    reproduce uno por uno al ritmo que decida: el backend no controla el tempo.
    """
    puntos_dominio = _a_dominio(payload.puntos)
    try:
        r = clasico.simular(
            puntos_dominio,
            cerrada=payload.cerrada,
            orden=payload.orden,
            semilla=payload.semilla,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _clasico_out(r)


@app.post("/api/v1/cuantico/simular", response_model=SimulacionCuanticaResponse)
def simular_cuantico(payload: SimulacionCuanticaRequest) -> SimulacionCuanticaResponse:
    """Corre la amplificacion de probabilidad y devuelve la traza completa.

    Cada paso trae la probabilidad de TODAS las rutas: todas siguen existiendo
    a la vez (superposicion) y el frontend las dibuja simultaneamente usando la
    probabilidad como opacidad.
    """
    puntos_dominio = _a_dominio(payload.puntos)
    try:
        r = cuantico.simular(
            puntos_dominio,
            cerrada=payload.cerrada,
            semilla=payload.semilla,
            iteraciones=payload.iteraciones,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _cuantico_out(r)


@app.get("/api/v1/escenario", response_model=EscenarioResponse)
def escenario(
    n: int = Query(5, ge=2, le=8),
    grid_size: int = Query(GRID_SIZE, ge=2, le=20),
    cerrada: bool = Query(False),
    orden: OrdenEvaluacion = Query(OrdenEvaluacion.SECUENCIAL),
    semilla: Optional[int] = Query(None),
) -> EscenarioResponse:
    """Genera el mapa y corre los DOS modos sobre el, en una sola llamada.

    Es el endpoint que conviene usar desde el frontend: al resolver todo de un
    tiro, ambos modos comparten los mismos puntos por construccion y no hay que
    coordinar semillas entre dos peticiones.
    """
    generados = _generar(n=n, grid_size=grid_size, semilla=semilla)
    try:
        r_clasico = clasico.simular(
            generados, cerrada=cerrada, orden=orden, semilla=semilla
        )
        r_cuantico = cuantico.simular(
            generados, cerrada=cerrada, semilla=semilla
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    salida_clasico = _clasico_out(r_clasico)
    salida_cuantico = _cuantico_out(r_cuantico)

    return EscenarioResponse(
        grid_size=grid_size,
        puntos=salida_clasico.puntos,
        rutas=salida_clasico.rutas,
        cerrada=cerrada,
        semilla=semilla,
        clasico=salida_clasico,
        cuantico=salida_cuantico,
        rutas_evaluadas_clasico=r_clasico.rutas_evaluadas,
        iteraciones_cuantico=r_cuantico.iteraciones,
    )


# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------


def _generar(n: int, grid_size: int, semilla: Optional[int]) -> List[Punto]:
    try:
        return generar_puntos(n=n, grid_size=grid_size, semilla=semilla)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


def _a_dominio(puntos) -> List[Punto]:
    ids = [p.id for p in puntos]
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=422, detail="los ids de los puntos deben ser unicos")
    return [Punto(id=p.id, x=p.x, y=p.y, etiqueta=p.etiqueta) for p in puntos]


def _clasico_out(r) -> SimulacionClasicaResponse:
    return SimulacionClasicaResponse(
        puntos=[p.__dict__ for p in r.puntos],
        rutas=[ruta.__dict__ for ruta in r.rutas],
        cerrada=r.cerrada,
        orden=r.orden,
        total_rutas=r.total_rutas,
        pasos=[paso.__dict__ for paso in r.pasos],
        mejor_ruta_id=r.mejor_ruta_id,
        mejor_ruta=r.mejor_ruta,
        mejor_distancia=r.mejor_distancia,
        rutas_evaluadas=r.rutas_evaluadas,
        empates_en_la_mejor=r.empates_en_la_mejor,
    )


def _cuantico_out(r) -> SimulacionCuanticaResponse:
    return SimulacionCuanticaResponse(
        puntos=[p.__dict__ for p in r.puntos],
        rutas=[ruta.__dict__ for ruta in r.rutas],
        cerrada=r.cerrada,
        total_rutas=r.total_rutas,
        pasos=[
            {
                "indice": paso.indice,
                "probabilidades": [pr.__dict__ for pr in paso.probabilidades],
                "visibles": paso.visibles,
                "eliminadas_en_esta_ronda": paso.eliminadas_en_esta_ronda,
                "probabilidad_marcadas": paso.probabilidad_marcadas,
            }
            for paso in r.pasos
        ],
        iteraciones=r.iteraciones,
        rutas_marcadas=r.rutas_marcadas,
        medicion_id=r.medicion_id,
        medicion_ruta=r.medicion_ruta,
        medicion_distancia=r.medicion_distancia,
        acerto=r.acerto,
        probabilidad_final_marcadas=r.probabilidad_final_marcadas,
    )
