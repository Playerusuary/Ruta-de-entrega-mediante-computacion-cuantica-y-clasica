"""Contrato de la API: lo que el backend promete y el frontend consume.

Este archivo es COMPARTIDO. La parte cuantica va a agregar aqui sus propios
esquemas de respuesta, pero PuntoOut y la forma de "una ruta es una lista de
ids" tienen que ser identicas en ambos modos para que el canvas pueda dibujar
las dos con el mismo codigo.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PuntoOut(BaseModel):
    """Un destino en el canvas."""

    id: int
    x: float
    y: float
    etiqueta: str = ""


class PuntosResponse(BaseModel):
    puntos: List[PuntoOut]
    ancho: int
    alto: int
    # Se devuelve para que el front la pueda reusar y montar exactamente el
    # mismo mapa en el modo cuantico.
    semilla: Optional[int] = None


class SimulacionRequest(BaseModel):
    """Cuerpo de POST /api/v1/clasico/simular."""

    puntos: List[PuntoOut] = Field(
        ...,
        min_length=2,
        max_length=8,
        description="Destinos; el primero es la base y queda fijo.",
    )
    cerrada: bool = Field(
        False,
        description=(
            "False: el dron termina en el ultimo punto (el caso del enunciado). "
            "True: escenario opcional donde regresa a la base."
        ),
    )


class PasoOut(BaseModel):
    """Un frame de la animacion: una ruta evaluada."""

    indice: int = Field(..., description="Contador de rutas evaluadas, arranca en 1.")
    ruta: List[int] = Field(..., description="Ids de los puntos en orden de recorrido.")
    distancia: float
    es_mejor: bool = Field(..., description="True si esta ruta rompio el record.")
    mejor_ruta: List[int]
    mejor_distancia: float


class SimulacionClasicaResponse(BaseModel):
    modo: str = "clasico"
    puntos: List[PuntoOut]
    cerrada: bool
    total_rutas: int = Field(..., description="(n-1)! con la base fija.")
    pasos: List[PasoOut] = Field(..., description="Traza completa, en orden de evaluacion.")
    mejor_ruta: List[int]
    mejor_distancia: float
    rutas_evaluadas: int
