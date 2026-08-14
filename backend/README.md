# Backend — simulador de ruta de entrega

La lógica vive aquí (Python). El frontend solo dibuja.

## Correr

```bash
cd backend
pip install -r requirements.txt      # fastapi, uvicorn, pydantic
python3 -m uvicorn app.main:app --reload --port 8000
```

Docs interactivas: <http://127.0.0.1:8000/docs>

## Pruebas

Corren con la stdlib, sin instalar nada extra:

```bash
cd backend
python3 -m unittest discover -s tests -v      # 53 pruebas
```

## Estructura

| Archivo | Dueño | Qué hace |
|---|---|---|
| `app/geometria.py` | **compartido** | Ciudad en cuadrícula, `Punto`, distancia Manhattan, permutaciones, catálogo de rutas. |
| `app/esquemas.py` | **compartido** | Contrato de la API (modelos Pydantic). |
| `app/clasico.py` | Parte 1 (bit) | Fuerza bruta: evalúa las rutas una por una. |
| `app/cuantico.py` | Parte 2 (qubit) | Amplificación de amplitud (Grover) sobre rutas. |
| `app/main.py` | compartido | App FastAPI, CORS y endpoints. |

> `geometria.py` y `esquemas.py` los usan **las dos partes**. Si la simulación
> clásica y la cuántica miden las rutas distinto, la comparación final no
> significa nada. Cambios ahí se acuerdan entre ambos.

## Modelo de ciudad

La ciudad es una **cuadrícula tipo Manhattan**: calles horizontales y verticales
que se cruzan en nodos de coordenadas enteras (`0..grid_size`). Los destinos caen
sobre esos nodos y el vehículo circula por las calles, nunca en diagonal.

La distancia es **Manhattan** (`|dx| + |dy|`) y no es configurable: el vehículo
circula por las calles, así que permitirle cortar en diagonal no sería fiel al
modelo.

Las coordenadas que expone la API son **de cuadrícula, no píxeles** — el
frontend las escala al canvas que quiera dibujar.

## Endpoints

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/health` | Salud. |
| `GET` | `/api/v1/puntos` | Genera el mapa. |
| `POST` | `/api/v1/clasico/simular` | Traza del modo clásico. |
| `POST` | `/api/v1/cuantico/simular` | Traza del modo cuántico. |
| `GET` | `/api/v1/escenario` | Mapa + los dos modos en una sola llamada. |

**Desde el frontend conviene usar `/escenario`**: al resolver todo de un tiro,
ambos modos comparten los mismos puntos por construcción y no hay que coordinar
semillas entre dos peticiones.

```bash
curl "http://127.0.0.1:8000/api/v1/escenario?n=5&semilla=42"
```

| Parámetro | Default | Nota |
|---|---|---|
| `n` | `5` | 2–8 destinos |
| `grid_size` | `6` | Manzanas por lado |
| `cerrada` | `false` | `true` = regresa al depósito |
| `orden` | `secuencial` | o `aleatorio` (modo clásico) |
| `semilla` | — | Fija el mapa y la medición final |

### Traza del modo clásico

```jsonc
{
  "rutas_evaluadas": 24,
  "mejor_ruta": [0, 3, 4, 1, 2],
  "mejor_distancia": 13.0,
  "empates_en_la_mejor": [16, 17],     // con Manhattan los empates son la norma
  "pasos": [
    {
      "indice": 1,                     // contador de rutas evaluadas
      "ruta_id": 0,
      "ruta": [0, 1, 2, 3, 4],
      "distancia": 24.0,
      "es_mejor": true,                // rompió el récord → resaltar este frame
      "mejor_ruta": [0, 1, 2, 3, 4],
      "mejor_distancia": 24.0
    }
    // ... 23 más
  ]
}
```

Se anima recorriendo `pasos` con un temporizador: se dibuja `paso.ruta` (una
sola ruta visible a la vez) y se mantiene `paso.mejor_ruta` resaltada al fondo.

### Traza del modo cuántico

```jsonc
{
  "iteraciones": 2,                    // consultas al oráculo
  "rutas_marcadas": [16, 17],
  "medicion_ruta": [0, 3, 4, 2, 1],
  "medicion_distancia": 13.0,
  "acerto": true,
  "probabilidad_final_marcadas": 0.9887,
  "pasos": [
    {
      "indice": 0,                     // 0 = superposición inicial
      "probabilidades": [              // TODAS las rutas, siempre presentes
        { "ruta_id": 0, "distancia": 24.0, "probabilidad": 0.041667 }
        // ... las 24
      ],
      "visibles": [/* ... */],
      "eliminadas_en_esta_ronda": [],
      "probabilidad_marcadas": 0.0833
    }
    // ... una entrada por iteración
  ]
}
```

Se anima dibujando **todas las rutas a la vez** y usando `probabilidad` como
opacidad. Ninguna ruta desaparece del arreglo — eso es la superposición; lo que
cambia es cuánto pesa cada una.

## Notas de diseño

### El backend manda la traza completa

Una sola llamada devuelve todos los frames ya ordenados. El servidor no guarda
estado, no hay round-trip por frame, y el tempo de la animación es decisión del
frontend. Pausar, acelerar o retroceder es cambiar un índice en un arreglo.

### El módulo clásico no se optimiza

Nada de vecino más cercano, programación dinámica ni poda por cota. Es el grupo
de control: si se vuelve listo, deja de medir lo que la comparación necesita
medir. Su trabajo es ser exhaustivo, no rápido.

### El número de iteraciones cuánticas no es arbitrario

Es el óptimo de Grover, `k = floor((π/4)·√(N/M))` con `N` rutas y `M` rutas
marcadas. Para 24 rutas con una sola ganadora da `k = 3` y ~98% de confianza.

**Pasarse empeora el resultado** — la amplitud vuelve a bajar. Es una propiedad
real del algoritmo y buen material para la presentación (`?iteraciones=` fuerza
el número para demostrarlo):

| Iteraciones | Confianza |
|---|---|
| 1 | 0.3345 |
| 2 | 0.7331 |
| **3 (óptimo)** | **0.9827** |
| 4 | 0.9240 |
| 6 | 0.2045 |
| 9 | 0.4788 |

### Los empates son la norma, no la excepción

Con distancia Manhattan sobre coordenadas enteras, varias rutas distintas miden
exactamente lo mismo (y en ruta cerrada, cada ruta y su reversa siempre
empatan). Por eso:

- El clásico reporta `empates_en_la_mejor`.
- El cuántico marca **todas** las mínimas y ajusta `k` según cuántas sean.
- Es normal que ambos modos devuelvan rutas **distintas** con la **misma**
  distancia. No es un bug: es un empate legítimo.

### Qué cambió respecto a la rama `Analisar`

La lógica cuántica se portó desde la rama del compañero conservando su idea de
reportar por ronda qué rutas siguen visibles y cuáles se desvanecen. Dos cosas
sí cambiaron, y **la última palabra sobre ellas es suya**:

1. **La ganadora ya no se inyecta.** Su versión recibía `mejor_ruta_id` ya
   calculado y lo protegía de la eliminación, así que la simulación no
   *encontraba* la ruta: se le entregaba. Ahora sale de las probabilidades.
2. **El número de rondas ya no es aleatorio.** Era `random.randint(4, 8)`,
   elegido para "verse rápido". Ahora se deriva de `N` y `M`.

Sobre la circularidad del oráculo: sí, para *simular* el oráculo hay que saber
cuáles rutas son mínimas. Eso es inherente a simular Grover en una máquina
clásica y no es trampa — en el modelo, el oráculo es una caja negra que reconoce
una solución sin que el buscador sepa cuál es. Lo que se cuenta y se compara
contra el modo clásico son las **consultas al oráculo**, que es justo donde
Grover afirma su ventaja: ~√N contra N.
