"""Pruebas de la simulacion cuantica (amplificacion de probabilidad).

Lo que mas importa aqui son dos cosas:

  1. Que las probabilidades se comporten como probabilidades (suman 1 siempre).
  2. Que el modo cuantico y el clasico coincidan en cual es la ruta mas corta.
     Si difieren, la comparacion del proyecto no vale nada.

    cd backend && python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import clasico, cuantico  # noqa: E402
from app.geometria import Punto, generar_puntos, medir_todas_las_rutas  # noqa: E402


class TestIteracionesOptimas(unittest.TestCase):
    def test_para_24_rutas_con_una_ganadora_son_3(self):
        # floor((pi/4) * sqrt(24)) = 3
        self.assertEqual(cuantico.iteraciones_optimas(24, 1), 3)

    def test_mas_rutas_marcadas_requieren_menos_iteraciones(self):
        self.assertLess(
            cuantico.iteraciones_optimas(24, 4), cuantico.iteraciones_optimas(24, 1)
        )

    def test_crece_como_raiz_de_n_no_como_n(self):
        # De 24 a 96 rutas (x4), las iteraciones apenas se duplican.
        self.assertEqual(cuantico.iteraciones_optimas(96, 1), 7)

    def test_casos_degenerados_dan_cero(self):
        self.assertEqual(cuantico.iteraciones_optimas(1, 1), 0)
        self.assertEqual(cuantico.iteraciones_optimas(0, 0), 0)


class TestSimulacionCuantica(unittest.TestCase):
    def test_arranca_en_superposicion_uniforme(self):
        r = cuantico.simular(generar_puntos(n=5, semilla=42))
        inicial = r.pasos[0]
        self.assertEqual(inicial.indice, 0)
        for pr in inicial.probabilidades:
            self.assertAlmostEqual(pr.probabilidad, 1 / 24, places=5)

    def test_todas_las_rutas_estan_presentes_en_cada_paso(self):
        # Superposicion: ninguna ruta desaparece del arreglo, solo baja su
        # probabilidad. Es lo que permite dibujarlas todas a la vez.
        r = cuantico.simular(generar_puntos(n=5, semilla=42))
        for paso in r.pasos:
            self.assertEqual(len(paso.probabilidades), 24)

    def test_las_probabilidades_suman_uno_en_cada_paso(self):
        r = cuantico.simular(generar_puntos(n=5, semilla=7))
        for paso in r.pasos:
            total = sum(pr.probabilidad for pr in paso.probabilidades)
            self.assertAlmostEqual(total, 1.0, places=4)

    def test_ninguna_probabilidad_es_negativa(self):
        r = cuantico.simular(generar_puntos(n=5, semilla=7))
        for paso in r.pasos:
            for pr in paso.probabilidades:
                self.assertGreaterEqual(pr.probabilidad, 0.0)

    def test_la_amplificacion_sube_la_probabilidad_de_las_marcadas(self):
        r = cuantico.simular(generar_puntos(n=5, semilla=42))
        self.assertGreater(r.pasos[-1].probabilidad_marcadas, r.pasos[0].probabilidad_marcadas)

    def test_la_confianza_crece_en_cada_iteracion(self):
        # Hasta el optimo, cada iteracion mejora. Pasarse es otro caso (abajo).
        r = cuantico.simular(generar_puntos(n=5, semilla=42))
        confianzas = [p.probabilidad_marcadas for p in r.pasos]
        for anterior, siguiente in zip(confianzas, confianzas[1:]):
            self.assertGreater(siguiente, anterior)

    def test_termina_con_alta_confianza(self):
        r = cuantico.simular(generar_puntos(n=5, semilla=42))
        self.assertGreater(r.probabilidad_final_marcadas, 0.9)

    def test_pasarse_del_optimo_empeora_el_resultado(self):
        # Propiedad clave de Grover y buen material para la presentacion:
        # mas iteraciones NO es mejor, la amplitud vuelve a bajar.
        puntos = generar_puntos(n=5, semilla=42)
        optimo = cuantico.simular(puntos)
        pasado = cuantico.simular(puntos, iteraciones=optimo.iteraciones * 3)
        self.assertLess(pasado.probabilidad_final_marcadas, optimo.probabilidad_final_marcadas)

    def test_las_rutas_marcadas_son_las_de_distancia_minima(self):
        puntos = generar_puntos(n=5, semilla=31)
        r = cuantico.simular(puntos, cerrada=True)
        minima = min(ruta.distancia for ruta in r.rutas)
        for rid in r.rutas_marcadas:
            self.assertAlmostEqual(r.rutas[rid].distancia, minima)

    def test_la_medicion_cae_en_una_ruta_existente(self):
        r = cuantico.simular(generar_puntos(n=5, semilla=42), semilla=1)
        self.assertTrue(0 <= r.medicion_id < len(r.rutas))
        self.assertEqual(r.medicion_ruta, r.rutas[r.medicion_id].orden)

    def test_la_medicion_es_reproducible_con_semilla(self):
        puntos = generar_puntos(n=5, semilla=42)
        a = cuantico.simular(puntos, semilla=123)
        b = cuantico.simular(puntos, semilla=123)
        self.assertEqual(a.medicion_id, b.medicion_id)

    def test_la_ganadora_no_se_inyecta_desde_afuera(self):
        # simular() no acepta ningun parametro con la respuesta: la ruta
        # marcada sale del propio catalogo de distancias.
        import inspect

        firma = inspect.signature(cuantico.simular).parameters
        for prohibido in ("mejor_ruta_id", "mejor", "ganadora"):
            self.assertNotIn(prohibido, firma)

    def test_la_vista_de_visibles_solo_se_encoge(self):
        r = cuantico.simular(generar_puntos(n=5, semilla=42))
        for anterior, siguiente in zip(r.pasos, r.pasos[1:]):
            self.assertLessEqual(len(siguiente.visibles), len(anterior.visibles))

    def test_menos_de_dos_puntos_es_error(self):
        with self.assertRaises(ValueError):
            cuantico.simular([Punto(id=0, x=0, y=0)])


class TestAcuerdoEntreLosDosModos(unittest.TestCase):
    """La prueba que sostiene todo el proyecto: ambos modos deben coincidir."""

    def _comparar(self, puntos, cerrada):
        c = clasico.simular(puntos, cerrada=cerrada)
        q = cuantico.simular(puntos, cerrada=cerrada)
        # Misma distancia minima encontrada.
        self.assertAlmostEqual(
            c.mejor_distancia, min(r.distancia for r in q.rutas), places=6
        )
        # El clasico eligio una de las rutas que el oraculo marca.
        self.assertIn(c.mejor_ruta_id, q.rutas_marcadas)
        # Y ambos evaluaron el mismo catalogo de rutas.
        self.assertEqual([r.orden for r in c.rutas], [r.orden for r in q.rutas])

    def test_coinciden_en_ruta_abierta(self):
        for semilla in range(8):
            self._comparar(generar_puntos(n=5, semilla=semilla), False)

    def test_coinciden_en_ruta_cerrada(self):
        for semilla in range(8):
            self._comparar(generar_puntos(n=5, semilla=semilla), True)

    def test_el_cuantico_usa_muchisimas_menos_consultas(self):
        # El titular del proyecto: 24 evaluaciones contra 2 o 3 iteraciones.
        # El numero exacto depende de cuantas rutas empatan en la minima (M),
        # y con distancia Manhattan sobre enteros los empates son la norma.
        for semilla in range(8):
            puntos = generar_puntos(n=5, semilla=semilla)
            c = clasico.simular(puntos)
            q = cuantico.simular(puntos)

            self.assertEqual(c.rutas_evaluadas, 24)
            self.assertEqual(
                q.iteraciones,
                cuantico.iteraciones_optimas(24, len(q.rutas_marcadas)),
            )
            self.assertLessEqual(q.iteraciones, 3)
            self.assertLess(q.iteraciones * 4, c.rutas_evaluadas)

    def test_la_confianza_final_es_alta_en_cualquier_mapa(self):
        for semilla in range(8):
            q = cuantico.simular(generar_puntos(n=5, semilla=semilla))
            self.assertGreater(q.probabilidad_final_marcadas, 0.9)

    def test_el_catalogo_de_rutas_es_identico_al_compartido(self):
        puntos = generar_puntos(n=5, semilla=2)
        compartido = medir_todas_las_rutas(puntos, cerrada=False)
        q = cuantico.simular(puntos)
        self.assertEqual([r.orden for r in compartido], [r.orden for r in q.rutas])


if __name__ == "__main__":
    unittest.main()
