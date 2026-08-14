"""Pruebas de la geometria compartida y de la simulacion clasica.

Se corren con la stdlib, sin instalar nada:

    cd backend && python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import clasico  # noqa: E402
from app.clasico import OrdenEvaluacion  # noqa: E402
from app.geometria import (  # noqa: E402
    Punto,
    distancia,
    generar_puntos,
    indices_mas_cortas,
    longitud_ruta,
    medir_todas_las_rutas,
    rutas_posibles,
    total_rutas,
)


def _cuadrado():
    """Cuatro esquinas de un cuadrado de lado 10, con el deposito en el origen.

    Sirve porque la respuesta se conoce a mano: recorrer el perimetro
    (0 -> 1 -> 2 -> 3) mide 30 abierto y 40 cerrado.
    """
    return [
        Punto(id=0, x=0, y=0, etiqueta="Base"),
        Punto(id=1, x=10, y=0, etiqueta="A"),
        Punto(id=2, x=10, y=10, etiqueta="B"),
        Punto(id=3, x=0, y=10, etiqueta="C"),
    ]


class TestGeometria(unittest.TestCase):
    def test_distancia_va_por_las_calles_no_en_diagonal(self):
        a, b = Punto(id=0, x=0, y=0), Punto(id=1, x=3, y=4)
        # Por calles son 3 + 4 = 7, no la diagonal euclidiana de 5.
        self.assertAlmostEqual(distancia(a, b), 7.0)

    def test_longitud_abierta_no_incluye_regreso(self):
        self.assertAlmostEqual(
            longitud_ruta(_cuadrado(), cerrada=False), 30.0
        )

    def test_longitud_cerrada_agrega_el_tramo_de_vuelta(self):
        self.assertAlmostEqual(
            longitud_ruta(_cuadrado(), cerrada=True), 40.0
        )

    def test_ruta_de_un_punto_mide_cero(self):
        self.assertEqual(longitud_ruta([Punto(id=0, x=5, y=5)]), 0.0)

    def test_total_rutas_es_factorial_de_n_menos_uno(self):
        self.assertEqual(total_rutas(5), 24)
        self.assertEqual(total_rutas(4), 6)
        self.assertEqual(total_rutas(8), 5040)

    def test_el_deposito_queda_fijo_en_todas_las_rutas(self):
        rutas = list(rutas_posibles(_cuadrado()))
        self.assertEqual(len(rutas), 6)  # 3! con el deposito fijo
        for ruta in rutas:
            self.assertEqual(ruta[0].id, 0)

    def test_las_rutas_generadas_no_se_repiten(self):
        rutas = [tuple(p.id for p in r) for r in rutas_posibles(_cuadrado())]
        self.assertEqual(len(rutas), len(set(rutas)))

    def test_cada_ruta_visita_todos_los_puntos_una_vez(self):
        puntos = _cuadrado()
        esperado = {p.id for p in puntos}
        for ruta in rutas_posibles(puntos):
            self.assertEqual({p.id for p in ruta}, esperado)
            self.assertEqual(len(ruta), len(puntos))

    def test_la_ruta_cerrada_vuelve_al_deposito_en_el_orden(self):
        rutas = medir_todas_las_rutas(_cuadrado(), cerrada=True)
        for r in rutas:
            self.assertEqual(r.orden[0], 0)
            self.assertEqual(r.orden[-1], 0)
            self.assertEqual(len(r.orden), 5)  # 4 puntos + regreso

    def test_la_ruta_abierta_no_repite_el_deposito(self):
        rutas = medir_todas_las_rutas(_cuadrado(), cerrada=False)
        for r in rutas:
            self.assertEqual(len(r.orden), 4)
            self.assertEqual(r.orden.count(0), 1)

    def test_indices_mas_cortas_detecta_empates(self):
        # En ruta cerrada, cada ruta y su reversa miden lo mismo.
        rutas = medir_todas_las_rutas(_cuadrado(), cerrada=True)
        marcadas = indices_mas_cortas(rutas)
        self.assertGreaterEqual(len(marcadas), 2)
        minima = min(r.distancia for r in rutas)
        for rid in marcadas:
            self.assertAlmostEqual(rutas[rid].distancia, minima)

    def test_los_puntos_caen_en_nodos_enteros_de_la_cuadricula(self):
        for p in generar_puntos(n=5, grid_size=6, semilla=7):
            self.assertEqual(p.x, int(p.x))
            self.assertEqual(p.y, int(p.y))
            self.assertTrue(0 <= p.x <= 6 and 0 <= p.y <= 6)

    def test_los_puntos_no_se_encinan(self):
        coords = [(p.x, p.y) for p in generar_puntos(n=8, grid_size=6, semilla=1)]
        self.assertEqual(len(coords), len(set(coords)))

    def test_misma_semilla_mismo_mapa(self):
        self.assertEqual(generar_puntos(n=5, semilla=42), generar_puntos(n=5, semilla=42))

    def test_semillas_distintas_dan_mapas_distintos(self):
        self.assertNotEqual(generar_puntos(n=5, semilla=1), generar_puntos(n=5, semilla=2))

    def test_no_caben_mas_puntos_que_nodos(self):
        # Una cuadricula de 2x2 tiene 9 nodos: 8 puntos caben.
        self.assertEqual(len(generar_puntos(n=8, grid_size=2, semilla=1)), 8)
        # 30 no.
        with self.assertRaises(ValueError):
            generar_puntos(n=30, grid_size=2)


class TestSimulacionClasica(unittest.TestCase):
    def test_evalua_todas_las_rutas_sin_saltarse_ninguna(self):
        r = clasico.simular(_cuadrado())
        self.assertEqual(r.total_rutas, 6)
        self.assertEqual(r.rutas_evaluadas, 6)
        self.assertEqual(len(r.pasos), 6)

    def test_con_cinco_puntos_evalua_24_rutas(self):
        r = clasico.simular(generar_puntos(n=5, semilla=42))
        self.assertEqual(r.total_rutas, 24)
        self.assertEqual(r.rutas_evaluadas, 24)

    def test_el_contador_avanza_de_uno_en_uno(self):
        r = clasico.simular(_cuadrado())
        self.assertEqual([p.indice for p in r.pasos], [1, 2, 3, 4, 5, 6])

    def test_encuentra_el_perimetro_como_ruta_mas_corta(self):
        r = clasico.simular(_cuadrado(), cerrada=False)
        self.assertAlmostEqual(r.mejor_distancia, 30.0)
        # 0->1->2->3 y 0->3->2->1 son el mismo perimetro recorrido al reves.
        self.assertIn(r.mejor_ruta, ([0, 1, 2, 3], [0, 3, 2, 1]))

    def test_el_minimo_coincide_con_el_minimo_de_toda_la_traza(self):
        r = clasico.simular(generar_puntos(n=5, semilla=99))
        self.assertAlmostEqual(r.mejor_distancia, min(p.distancia for p in r.pasos))

    def test_el_mejor_hasta_ahora_nunca_empeora(self):
        r = clasico.simular(generar_puntos(n=5, semilla=3))
        distancias = [p.mejor_distancia for p in r.pasos]
        for anterior, siguiente in zip(distancias, distancias[1:]):
            self.assertLessEqual(siguiente, anterior)

    def test_es_mejor_marca_exactamente_los_frames_que_rompen_el_record(self):
        r = clasico.simular(generar_puntos(n=5, semilla=11))
        record = math.inf
        for paso in r.pasos:
            self.assertEqual(paso.es_mejor, paso.distancia < record)
            record = min(record, paso.distancia)

    def test_el_primer_paso_siempre_es_mejor(self):
        r = clasico.simular(generar_puntos(n=5, semilla=5))
        self.assertTrue(r.pasos[0].es_mejor)

    def test_la_mejor_distancia_coincide_con_las_rutas_marcadas(self):
        r = clasico.simular(generar_puntos(n=5, semilla=13), cerrada=True)
        for rid in r.empates_en_la_mejor:
            self.assertAlmostEqual(r.rutas[rid].distancia, r.mejor_distancia)
        self.assertIn(r.mejor_ruta_id, r.empates_en_la_mejor)

    def test_la_ruta_cerrada_nunca_mide_menos_que_la_abierta(self):
        puntos = generar_puntos(n=5, semilla=21)
        abierta = clasico.simular(puntos, cerrada=False)
        cerrada = clasico.simular(puntos, cerrada=True)
        self.assertGreater(cerrada.mejor_distancia, abierta.mejor_distancia)
        self.assertEqual(cerrada.rutas_evaluadas, abierta.rutas_evaluadas)

    def test_orden_aleatorio_evalua_el_mismo_conjunto(self):
        puntos = generar_puntos(n=5, semilla=8)
        sec = clasico.simular(puntos, orden=OrdenEvaluacion.SECUENCIAL)
        alea = clasico.simular(puntos, orden=OrdenEvaluacion.ALEATORIO, semilla=8)
        self.assertEqual(
            sorted(p.ruta_id for p in sec.pasos),
            sorted(p.ruta_id for p in alea.pasos),
        )
        # Y encuentran la misma distancia minima, aunque en distinto momento.
        self.assertAlmostEqual(sec.mejor_distancia, alea.mejor_distancia)

    def test_orden_aleatorio_es_reproducible_con_semilla(self):
        puntos = generar_puntos(n=5, semilla=8)
        a = clasico.simular(puntos, orden=OrdenEvaluacion.ALEATORIO, semilla=77)
        b = clasico.simular(puntos, orden=OrdenEvaluacion.ALEATORIO, semilla=77)
        self.assertEqual([p.ruta_id for p in a.pasos], [p.ruta_id for p in b.pasos])

    def test_dos_corridas_iguales_dan_la_misma_traza(self):
        puntos = generar_puntos(n=5, semilla=8)
        a = clasico.simular(puntos)
        b = clasico.simular(puntos)
        self.assertEqual([p.ruta for p in a.pasos], [p.ruta for p in b.pasos])

    def test_menos_de_dos_puntos_es_error(self):
        with self.assertRaises(ValueError):
            clasico.simular([Punto(id=0, x=0, y=0)])


if __name__ == "__main__":
    unittest.main()
