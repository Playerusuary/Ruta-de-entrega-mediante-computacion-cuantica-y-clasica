"""Contrato de la API: lo que el backend promete y el frontend consume.

Este archivo es COMPARTIDO. PuntoOut, RutaOut y la forma de "una ruta es una
lista de ids" tienen que ser identicas en ambos modos para que el canvas pueda
dibujar los dos con el mismo codigo.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .clasico import OrdenEvaluacion
from .geometria import GRID_SIZE


class PuntoOut(BaseModel):
    """Un destino sobre un nodo de la cuadricula.

    x e y son coordenadas de CUADRICULA (enteras, 0..grid_size), no pixeles.
    El frontend las escala al canvas que quiera dibujar.
    """

    id: int
    x: float
    y: float
    etiqueta: str = ""


class RutaOut(BaseModel):
    """Una ruta del catalogo compartido por ambos modos."""

    id: int
    orden: List[int] = Field(..., description="Ids de los puntos en orden de recorrido.")
    distancia: float


class PuntosResponse(BaseModel):
    puntos: List[PuntoOut]
    grid_size: int = GRID_SIZE
    # Se devuelve para que el front la pueda reusar y montar exactamente el
    # mismo mapa en el otro modo.
    semilla: Optional[int] = None


class _BaseSimulacionRequest(BaseModel):
    puntos: List[PuntoOut] = Field(
        ...,
        min_length=2,
        max_length=8,
        description="Destinos; el primero es el deposito y queda fijo.",
    )
    cerrada: bool = Field(
        False,
        description=(
            "False: el vehiculo termina en el ultimo punto (el caso del enunciado). "
            "True: escenario opcional donde regresa al deposito."
        ),
    )
    semilla: Optional[int] = None


class SimulacionClasicaRequest(_BaseSimulacionRequest):
    orden: OrdenEvaluacion = Field(
        OrdenEvaluacion.SECUENCIAL,
        description="secuencial (default) o aleatorio, como en la rama del compañero.",
    )


class SimulacionCuanticaRequest(_BaseSimulacionRequest):
    iteraciones: Optional[int] = Field(
        None,
        ge=0,
        le=50,
        description=(
            "Forzar el numero de iteraciones. None = usar el optimo de Grover. "
            "Sirve para demostrar que pasarse del optimo empeora el resultado."
        ),
    )


class PasoClasicoOut(BaseModel):
    """Un frame del modo clasico: una ruta evaluada."""

    indice: int = Field(..., description="Contador de rutas evaluadas, arranca en 1.")
    ruta_id: int
    ruta: List[int]
    distancia: float
    es_mejor: bool = Field(..., description="True si esta ruta rompio el record.")
    mejor_ruta: List[int]
    mejor_distancia: float


class SimulacionClasicaResponse(BaseModel):
    modo: str = "clasico"
    puntos: List[PuntoOut]
    rutas: List[RutaOut]
    cerrada: bool
    orden: OrdenEvaluacion
    total_rutas: int = Field(..., description="(n-1)! con el deposito fijo.")
    pasos: List[PasoClasicoOut] = Field(..., description="Traza completa, en orden de evaluacion.")
    mejor_ruta_id: int
    mejor_ruta: List[int]
    mejor_distancia: float
    rutas_evaluadas: int
    empates_en_la_mejor: List[int]


class ProbabilidadRutaOut(BaseModel):
    ruta_id: int
    distancia: float
    probabilidad: float


class PasoCuanticoOut(BaseModel):
    """Un frame del modo cuantico: una iteracion de amplificacion."""

    indice: int = Field(..., description="0 = superposicion inicial; luego 1, 2, 3...")
    probabilidades: List[ProbabilidadRutaOut] = Field(
        ...,
        description="Probabilidad de TODAS las rutas; usar como opacidad al dibujar.",
    )
    visibles: List[int]
    eliminadas_en_esta_ronda: List[int]
    probabilidad_marcadas: float


class SimulacionCuanticaResponse(BaseModel):
    modo: str = "cuantico"
    puntos: List[PuntoOut]
    rutas: List[RutaOut]
    cerrada: bool
    total_rutas: int
    pasos: List[PasoCuanticoOut]
    iteraciones: int = Field(
        ...,
        description="Consultas al oraculo. Es el numero a comparar contra rutas_evaluadas.",
    )
    rutas_marcadas: List[int]
    medicion_id: int
    medicion_ruta: List[int]
    medicion_distancia: float
    acerto: bool = Field(..., description="Si la medicion cayo en una ruta marcada.")
    probabilidad_final_marcadas: float


class EscenarioResponse(BaseModel):
    """Todo lo necesario para animar los dos modos sobre el mismo mapa.

    Una sola llamada garantiza por construccion que ambos modos corren sobre
    los mismos puntos, sin que el frontend tenga que coordinar semillas.
    """

    grid_size: int
    puntos: List[PuntoOut]
    rutas: List[RutaOut]
    cerrada: bool
    semilla: Optional[int] = None
    clasico: SimulacionClasicaResponse
    cuantico: SimulacionCuanticaResponse
    # El titular de la comparacion: cuanto le costo a cada modo.
    rutas_evaluadas_clasico: int
    iteraciones_cuantico: int
