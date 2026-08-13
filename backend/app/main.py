"""API del simulador de ruta de entrega.

El backend hace la logica (permutaciones, distancias, traza) y el frontend solo
dibuja. Cada endpoint responde en una sola llamada con todo lo que el canvas
necesita para animar, sin estado de sesion en el servidor.
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import clasico
from .esquemas import (
    PasoOut,
    PuntosResponse,
    SimulacionClasicaResponse,
    SimulacionRequest,
)
from .geometria import Punto, generar_puntos

app = FastAPI(
    title="Ruta de entrega - cuantica vs clasica",
    description="Simulador de mini TSP (4-5 puntos) en modo clasico y cuantico.",
    version="0.1.0",
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
    ancho: int = Query(800, ge=200, le=2000),
    alto: int = Query(600, ge=200, le=2000),
    semilla: Optional[int] = Query(
        None,
        description=(
            "Fija el mapa. Con la misma semilla, el modo clasico y el cuantico "
            "corren sobre exactamente los mismos puntos."
        ),
    ),
) -> PuntosResponse:
    """Genera un mapa de destinos al azar (o reproducible, si mandas semilla)."""
    try:
        generados = generar_puntos(n=n, ancho=ancho, alto=alto, semilla=semilla)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return PuntosResponse(
        puntos=[p.__dict__ for p in generados],
        ancho=ancho,
        alto=alto,
        semilla=semilla,
    )


@app.post("/api/v1/clasico/simular", response_model=SimulacionClasicaResponse)
def simular_clasico(payload: SimulacionRequest) -> SimulacionClasicaResponse:
    """Corre la simulacion clasica y devuelve la traza completa.

    La respuesta trae los (n-1)! pasos en orden de evaluacion. El frontend los
    reproduce uno por uno al ritmo que decida: el backend no controla el tempo.
    """
    puntos_dominio = [
        Punto(id=p.id, x=p.x, y=p.y, etiqueta=p.etiqueta) for p in payload.puntos
    ]

    ids = [p.id for p in puntos_dominio]
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=422, detail="los ids de los puntos deben ser unicos")

    try:
        resultado = clasico.simular(puntos_dominio, cerrada=payload.cerrada)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return SimulacionClasicaResponse(
        puntos=[p.__dict__ for p in resultado.puntos],
        cerrada=resultado.cerrada,
        total_rutas=resultado.total_rutas,
        pasos=[PasoOut(**paso.__dict__) for paso in resultado.pasos],
        mejor_ruta=resultado.mejor_ruta,
        mejor_distancia=resultado.mejor_distancia,
        rutas_evaluadas=resultado.rutas_evaluadas,
    )
