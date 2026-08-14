# Ruta de entrega mediante computación cuántica y clásica

> Simulador visual de una ruta de entrega óptima (mini TSP) sobre una ciudad en
> cuadrícula, resuelta de dos formas sobre el mismo mapa: **fuerza bruta clásica
> (bit)** y **amplificación de probabilidad cuántica (qubit)**.

El objetivo no es solo encontrar la ruta más corta, sino **hacer visible la
diferencia** entre cómo la busca un bit y cómo la busca un qubit: uno evalúa una
ruta a la vez, el otro las mantiene todas en superposición y va desvaneciendo
las malas.

**El titular:** para 5 puntos, el modo clásico evalúa **24 rutas**; el cuántico
converge en **2 o 3 iteraciones** con ~98% de confianza.

---

## Índice

- [Stack tecnológico](#stack-tecnológico)
- [Estado del proyecto](#estado-del-proyecto)
- [Cómo correrlo](#cómo-correrlo)
- [Modelo de ciudad](#modelo-de-ciudad)
- [Arquitectura](#arquitectura)
- [La API](#la-api)
- [Reglas de convivencia](#reglas-de-convivencia)
- [Qué cambió al integrar la rama `Analisar`](#qué-cambió-al-integrar-la-rama-analisar)
- [Especificación del caso](#especificación-del-caso)

---

## Stack tecnológico

La lógica vive en **Python**; el frontend **solo dibuja**. Toda permutación,
distancia y probabilidad se calcula en el backend y viaja por API.

### Backend — lógica

| Tecnología | Versión | Rol |
|---|---|---|
| Python | 3.9.6 | Lenguaje de la lógica |
| FastAPI | 0.128.8 | API HTTP + docs automáticas |
| Pydantic | 2.13.4 | Contrato y validación de datos |
| Uvicorn | 0.39.0 | Servidor ASGI |
| `unittest` | stdlib | Pruebas (sin dependencias extra) |

### Frontend — visualización

| Tecnología | Versión | Rol |
|---|---|---|
| Next.js | 16.3.0 | Framework (App Router) |
| React | 19.2.8 | UI |
| TypeScript | 5.x | Lenguaje |
| Tailwind CSS | 4.x | Estilos |
| Biome | 2.4.2 | Lint y formato |

---

## Estado del proyecto

| Componente | Responsable | Estado |
|---|---|---|
| Geometría compartida (cuadrícula, métricas, catálogo de rutas) | — compartido — | ✅ Listo |
| Contrato de la API (esquemas Pydantic) | — compartido — | ✅ Listo |
| Generador de mapas con semilla reproducible | — compartido — | ✅ Listo |
| **Parte 1 — Simulación clásica (bit)**, backend | Daniel | ✅ Listo |
| **Parte 2 — Simulación cuántica (qubit)**, backend | compañero | ✅ Portado · **pendiente su revisión** |
| Endpoint `/escenario` (ambos modos en una llamada) | compartido | ✅ Listo |
| Pruebas del backend | compartido | ✅ 57 pruebas |
| Canvas compartido (cuadrícula + puntos + rutas) | compartido | ⬜ Pendiente |
| Frontend Parte 1 (animación clásica) | Daniel | ⬜ Pendiente |
| Frontend Parte 2 (animación cuántica) | compañero | ⬜ Pendiente |

> El backend está completo y verificado end-to-end. El frontend sigue siendo el
> scaffold por defecto de Next.js: los componentes de la rama `Analisar`
> (`CityMap`, `Controles`, `useSimulacion`) están pendientes de portar.

---

## Cómo correrlo

### Backend

```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --port 8000
```

Docs interactivas (Swagger): <http://127.0.0.1:8000/docs>

### Pruebas

Corren con la librería estándar, sin instalar nada extra:

```bash
cd backend
python3 -m unittest discover -s tests -v      # 57 pruebas
```

### Frontend

```bash
cd frontend
npm install
npm run dev            # http://localhost:3000
```

El backend ya trae CORS habilitado para `localhost:3000`.

---

## Modelo de ciudad

La ciudad es una **cuadrícula tipo Manhattan**: calles horizontales y verticales
que se cruzan en nodos de coordenadas enteras (`0..grid_size`, por defecto 6).
Los destinos caen sobre esos nodos y el vehículo circula por las calles, nunca
en diagonal.

Este modelo viene de la rama del compañero y encaja mejor con el *"mapa tipo
maps"* del enunciado que un canvas libre con distancia en línea recta.

| Métrica | Fórmula | Cuándo |
|---|---|---|
| `manhattan` (default) | `\|dx\| + \|dy\|` | El vehículo va por las calles. |
| `euclidiana` | `√(dx² + dy²)` | Línea recta; sirve para contrastar. |

Las coordenadas que expone la API son **de cuadrícula, no píxeles** — el
frontend las escala al canvas que quiera dibujar.

> **Ambos modos deben correr con la misma métrica.** Es la primera forma de
> arruinar la comparación sin darse cuenta.

---

## Arquitectura

```
.
├── backend/                    Lógica en Python
│   ├── app/
│   │   ├── geometria.py        ← COMPARTIDO  cuadrícula, métricas, catálogo de rutas
│   │   ├── esquemas.py         ← COMPARTIDO  contrato de la API (Pydantic)
│   │   ├── clasico.py          ← Parte 1     fuerza bruta, una ruta a la vez
│   │   ├── cuantico.py         ← Parte 2     amplificación de amplitud (Grover)
│   │   └── main.py             ← COMPARTIDO  app FastAPI, CORS, endpoints
│   ├── tests/
│   └── requirements.txt
│
└── frontend/                   Visualización en Next.js
    └── src/app/
```

### Decisión de diseño: el backend manda la traza completa

La simulación **no** se pide paso por paso. Una sola llamada devuelve **todos
los frames ya ordenados** y el frontend los reproduce al ritmo que quiera.

1. El servidor **no guarda estado** entre frames.
2. **No hay round-trip de red por frame** — la animación no depende de la latencia.
3. **El tempo es decisión del frontend.** Pausar, acelerar o retroceder es
   cambiar un índice en un arreglo.

---

## La API

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/health` | Salud. |
| `GET` | `/api/v1/puntos` | Genera el mapa. |
| `POST` | `/api/v1/clasico/simular` | Traza del modo clásico. |
| `POST` | `/api/v1/cuantico/simular` | Traza del modo cuántico. |
| `GET` | `/api/v1/escenario` | Mapa + los dos modos en una sola llamada. |

**Desde el frontend conviene usar `/escenario`.** Al resolver todo de un tiro,
ambos modos comparten los mismos puntos por construcción y no hay que coordinar
semillas entre dos peticiones. La idea viene de la rama del compañero.

```bash
curl "http://127.0.0.1:8000/api/v1/escenario?n=5&semilla=42"
```

| Parámetro | Default | Nota |
|---|---|---|
| `n` | `5` | 2–8 destinos |
| `grid_size` | `6` | Manzanas por lado |
| `cerrada` | `false` | `true` = regresa al depósito |
| `metrica` | `manhattan` | o `euclidiana` |
| `orden` | `secuencial` | o `aleatorio` (modo clásico) |
| `semilla` | — | Fija el mapa y la medición final |

### Cómo se anima cada modo

**Clásico** — recorrer `pasos` con un temporizador. En cada frame se dibuja
`paso.ruta` (**una sola ruta visible a la vez**), se muestra `paso.indice` como
contador, y se mantiene `paso.mejor_ruta` resaltada al fondo. Cuando `es_mejor`
es `true`, ese frame merece énfasis.

**Cuántico** — dibujar **todas las rutas a la vez** usando
`probabilidades[].probabilidad` como opacidad. Ninguna ruta desaparece del
arreglo: eso es la superposición. Lo que cambia es cuánto pesa cada una.

El detalle completo de ambas respuestas está en
[backend/README.md](backend/README.md).

### Los empates son la norma, no la excepción

Con métrica Manhattan sobre coordenadas enteras, varias rutas distintas miden
exactamente lo mismo (y en ruta cerrada, cada ruta y su reversa **siempre**
empatan). Por eso el clásico reporta `empates_en_la_mejor` y el cuántico marca
todas las mínimas.

**Es normal que ambos modos devuelvan rutas distintas con la misma distancia.**
No es un bug: es un empate legítimo, y conviene saberlo antes de la exposición.

---

## Reglas de convivencia

Somos dos personas sobre el mismo canvas y el mismo backend. Cuatro acuerdos:

**1. `geometria.py` y `esquemas.py` son territorio compartido.**
Si la simulación clásica y la cuántica miden las rutas distinto, la comparación
final no significa nada. Cambios ahí se avisan antes.

**2. `clasico.py` no se optimiza. Nunca.**
Nada de vecino más cercano, programación dinámica ni poda por cota. Es
deliberadamente exhaustivo porque es el **grupo de control**. El módulo tiene
esa advertencia escrita en el encabezado.

**3. Los dos modos corren sobre el mismo mapa y la misma métrica.**
Usando `/escenario` sale gratis.

**4. Ramas de integración, no commits directos a `main` cuando el cambio toca
lo compartido.** Así nadie se baja un estado a medias.

---

## Qué cambió al integrar la rama `Analisar`

La rama del compañero era un historial independiente (sin ancestro común con
`main`) que reimplementaba el proyecto completo. Se combinó tomando lo mejor de
cada lado.

### Lo que se adoptó de su rama

| Suyo | Por qué |
|---|---|
| **Ciudad en cuadrícula + distancia Manhattan** | Más fiel al *"mapa tipo maps"*: un vehículo de reparto circula por calles, no en diagonal. |
| **Una sola llamada resuelve todo el escenario** | Garantiza por construcción que ambos modos comparten el mapa. Quedó como `/api/v1/escenario`. |
| **Vista de "visibles / eliminadas por ronda"** | Se conserva en la traza cuántica para que su frontend siga sirviendo. |
| **Orden aleatorio de evaluación** | Quedó como opción `orden=aleatorio` del modo clásico. |

### Lo que se conservó de nuestro stack

Paquete `app/` con módulos separados, esquemas Pydantic tipados, mapas
reproducibles por semilla, traza completa en una llamada, y la batería de
pruebas (ahora 57).

### Dos cambios en su lógica cuántica — **la última palabra es suya**

1. **La ganadora ya no se inyecta.** Su versión recibía `mejor_ruta_id` ya
   calculado y lo protegía de la eliminación, así que la simulación no
   *encontraba* la ruta: se le entregaba y coreografiaba el desvanecimiento
   alrededor. Ahora la ganadora sale de las probabilidades.

2. **El número de rondas ya no es aleatorio.** Era `random.randint(4, 8)`,
   elegido para "verse rápido". Ahora es el óptimo de Grover,
   `k = floor((π/4)·√(N/M))`.

Además se implementaron las **probabilidades** que pide el enunciado (inicial
`1/N`, amplificada por iteración) y la **medición final ponderada**, que su
versión no tenía: eliminaba rutas por conjuntos, sin probabilidad asociada.

> **Sobre la circularidad del oráculo:** sí, para *simular* el oráculo hay que
> saber cuáles rutas son mínimas. Eso es inherente a simular Grover en una
> máquina clásica y no es trampa — en el modelo, el oráculo es una caja negra
> que reconoce una solución sin que el buscador sepa cuál es. Lo que se cuenta y
> se compara contra el modo clásico son las **consultas al oráculo**, que es
> justo donde Grover afirma su ventaja: ~√N contra N.

### Un regalo para la presentación

Pasarse del número óptimo de iteraciones **empeora** el resultado: la amplitud
vuelve a bajar. Es una propiedad real del algoritmo, y el parámetro
`?iteraciones=` permite demostrarla en vivo:

| Iteraciones | Confianza |
|---|---|
| 1 | 0.3345 |
| 2 | 0.7331 |
| **3 (óptimo)** | **0.9827** |
| 4 | 0.9240 |
| 6 | 0.2045 |
| 9 | 0.4788 |

---

## Especificación del caso

> **Caso 3 — Ruta óptima de entrega (mini TSP, 4 a 5 puntos)**

**Problemática.** Un dron de entrega debe visitar 4 o 5 puntos siguiendo la ruta
más corta posible.

**Mecanismo cuántico.** A — Amplificación de probabilidad (aplicada a rutas en
vez de casillas).

**Entrada.** Coordenadas de 4-5 puntos en un canvas (fijas o generadas al azar
al reiniciar).

**Salida esperada.** La ruta más corta encontrada por cada modo y cuántos
caminos evaluó cada uno.

### Parte 1 — Simulación clásica (bit)

- Calcular todas las permutaciones posibles de los puntos (para 5 puntos son
  4! = 24 rutas, fijando el punto de partida).
- Dibujar cada ruta una por una sobre el mapa, calculando su distancia total, y
  llevar un contador de rutas evaluadas.
- Al terminar, resaltar la ruta de menor distancia total encontrada.

### Parte 2 — Simulación cuántica (qubit)

- Generar el mismo conjunto de rutas posibles (las mismas permutaciones) pero
  dibujarlas todas a la vez, semi-transparentes, sobre el mismo mapa — esto
  representa la superposición.
- Asignar a cada ruta una probabilidad inicial igual (1 / total de rutas).
- En cada iteración, aplicar el Mecanismo A: subir la probabilidad de la ruta
  más corta (la que cumple la condición) y bajar la de las demás; reflejar esto
  visualmente bajando la opacidad de las rutas menos probables en cada paso,
  hasta que solo quede una brillante.
- Medir al final con la función ponderada y resaltar la ruta resultante como la
  elegida.

### Elementos visuales obligatorios

- Mapa o canvas con los puntos y líneas de ruta dibujadas.
- **Modo clásico:** una sola ruta visible a la vez, cambiando en cada intento.
- **Modo cuántico:** todas las rutas visibles a la vez, desvaneciéndose las
  malas iteración a iteración.
- Contador de **rutas evaluadas** (clásico) vs. **iteraciones** (cuántico).
