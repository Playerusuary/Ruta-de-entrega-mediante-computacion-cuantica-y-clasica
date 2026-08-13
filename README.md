# Ruta de entrega mediante computación cuántica y clásica

> Simulador visual de una ruta de entrega óptima (mini TSP), resuelta de dos
> formas sobre el mismo mapa: **fuerza bruta clásica (bit)** y **amplificación
> de probabilidad cuántica (qubit)**.

El objetivo no es solo encontrar la ruta más corta, sino **hacer visible la
diferencia** entre cómo la busca un bit y cómo la busca un qubit: uno evalúa una
ruta a la vez, el otro las mantiene todas en superposición y va desvaneciendo
las malas.

---

## Índice

- [Stack tecnológico](#stack-tecnológico)
- [Estado del proyecto](#estado-del-proyecto)
- [Cómo correrlo](#cómo-correrlo)
- [Arquitectura](#arquitectura)
- [La API](#la-api)
- [Reglas de convivencia](#reglas-de-convivencia)
- [Para arrancar la Parte 2](#para-arrancar-la-parte-2-cuántica)
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
| Geometría compartida (`Punto`, distancias, permutaciones) | — compartido — | ✅ Listo |
| Contrato de la API (esquemas Pydantic) | — compartido — | ✅ Listo |
| Generador de mapas con semilla reproducible | — compartido — | ✅ Listo |
| **Parte 1 — Simulación clásica (bit)**, backend | Daniel | ✅ Listo · 23 pruebas |
| **Parte 2 — Simulación cuántica (qubit)**, backend | compañero | ⬜ Pendiente |
| Canvas compartido (puntos + rutas) | compartido | ⬜ Pendiente |
| Frontend Parte 1 (animación clásica) | Daniel | ⬜ Pendiente |
| Frontend Parte 2 (animación cuántica) | compañero | ⬜ Pendiente |

> El frontend es todavía el scaffold por defecto de Next.js: no hay canvas aún.
> El backend de la Parte 1 está funcionando y verificado end-to-end.

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
python3 -m unittest discover -s tests -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev            # http://localhost:3000
```

El backend ya trae CORS habilitado para `localhost:3000`.

---

## Arquitectura

```
.
├── backend/                    Lógica en Python
│   ├── app/
│   │   ├── geometria.py        ← COMPARTIDO  Punto, distancia, permutaciones, mapas
│   │   ├── esquemas.py         ← COMPARTIDO  contrato de la API (Pydantic)
│   │   ├── clasico.py          ← Parte 1     fuerza bruta, una ruta a la vez
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

Esto tiene tres consecuencias que conviene entender antes de tocar el front:

1. El servidor **no guarda estado** entre frames.
2. **No hay un round-trip de red por ruta dibujada** — la animación no depende
   de la latencia.
3. **El tempo es decisión del frontend**, no del backend. Pausar, acelerar o
   retroceder la animación es cambiar un índice en un arreglo.

La Parte 2 debería seguir el mismo patrón: devolver la lista de iteraciones con
las probabilidades de cada ruta en cada paso, y dejar que el canvas las
reproduzca.

---

## La API

### `GET /api/v1/puntos`

Genera el mapa de destinos.

| Parámetro | Default | Nota |
|---|---|---|
| `n` | `5` | 2–8 destinos |
| `ancho` / `alto` | `800` / `600` | Tamaño del canvas en píxeles |
| `semilla` | — | Fija el mapa de forma reproducible |

El primer punto (`id: 0`, etiqueta `Base`) es la base y **queda fijo**: es lo que
reduce 5! = 120 permutaciones a 4! = 24 rutas.

> **La semilla es importante para el proyecto.** Pasando la misma semilla, el
> modo clásico y el cuántico corren sobre **exactamente los mismos puntos**.
> Comparar 24 rutas contra N iteraciones sobre mapas distintos no probaría nada.

```jsonc
// GET /api/v1/puntos?n=5&semilla=42
{
  "puntos": [
    { "id": 0, "x": 494.81, "y": 72.01,  "etiqueta": "Base" },
    { "id": 1, "x": 247.02, "y": 167.14, "etiqueta": "A" },
    { "id": 2, "x": 560.80, "y": 384.82, "etiqueta": "B" },
    { "id": 3, "x": 666.68, "y": 101.73, "etiqueta": "C" },
    { "id": 4, "x": 346.91, "y": 74.30,  "etiqueta": "D" }
  ],
  "ancho": 800, "alto": 600, "semilla": 42
}
```

### `POST /api/v1/clasico/simular`

Corre la simulación clásica y devuelve la traza completa.

```jsonc
// request
{
  "puntos": [ /* los mismos del endpoint anterior */ ],
  "cerrada": false        // true = el dron regresa a la base (escenario opcional)
}
```

```jsonc
// response
{
  "modo": "clasico",
  "total_rutas": 24,               // (n-1)! con la base fija
  "rutas_evaluadas": 24,
  "mejor_ruta": [0, 4, 1, 2, 3],
  "mejor_distancia": 968.43,
  "pasos": [                       // la traza completa, en orden de evaluación
    {
      "indice": 1,                    // contador de rutas evaluadas
      "ruta": [0, 1, 2, 3, 4],        // ids en orden de recorrido
      "distancia": 1270.5,
      "es_mejor": true,               // rompió el récord → resaltar este frame
      "mejor_ruta": [0, 1, 2, 3, 4],  // campeona vigente tras este paso
      "mejor_distancia": 1270.5
    }
    // ... 23 pasos más
  ]
}
```

**Cómo se anima:** recorrer `pasos` con un temporizador. En cada frame se dibuja
`paso.ruta` (una sola ruta visible a la vez), se muestra `paso.indice` como
contador, y se mantiene `paso.mejor_ruta` resaltada en segundo plano. Cuando
`es_mejor` es `true`, ese frame merece énfasis visual.

---

## Reglas de convivencia

Somos dos personas sobre el mismo canvas y el mismo backend. Tres acuerdos:

**1. `geometria.py` y `esquemas.py` son territorio compartido.**
Si la simulación clásica y la cuántica miden las rutas distinto, la comparación
final no significa nada. Cambios ahí se avisan antes.

**2. `clasico.py` no se optimiza. Nunca.**
Nada de vecino más cercano, programación dinámica ni poda por cota. Es
deliberadamente exhaustivo porque es el **grupo de control**: si el clásico se
vuelve listo, deja de medir lo que la comparación necesita medir. El módulo
tiene esa advertencia escrita en el encabezado.

**3. Las dos partes corren sobre la misma semilla.**
Es la única forma de que la comparación sea justa.

---

## Para arrancar la Parte 2 (cuántica)

Lo que ya está hecho y **se puede reutilizar tal cual**:

| Ya disponible en `app/geometria.py` | Para qué sirve en la Parte 2 |
|---|---|
| `rutas_posibles(puntos)` | Genera **el mismo conjunto** de permutaciones que usa el clásico — es justo lo que pide el enunciado para la superposición. |
| `longitud_ruta(ruta, cerrada)` | Mide cada ruta con la misma fórmula que el clásico. |
| `total_rutas(n)` | `(n-1)!` — el denominador de la probabilidad inicial `1/total`. |
| `generar_puntos(n, semilla=...)` | El mismo mapa que el clásico, si se usa la misma semilla. |
| `Punto` | El tipo compartido. |

Con eso, la probabilidad inicial de cada ruta es literalmente
`1 / total_rutas(len(puntos))`, y las rutas a superponer salen de
`rutas_posibles(puntos)`.

### Forma sugerida para el endpoint

Espejo del clásico, para que el canvas pueda dibujar ambos modos con el mismo
código. **Es una propuesta, no está implementada — ajústala a tu criterio:**

```jsonc
// POST /api/v1/cuantico/simular
{
  "modo": "cuantico",
  "total_rutas": 24,
  "iteraciones_ejecutadas": 4,
  "mejor_ruta": [0, 4, 1, 2, 3],
  "mejor_distancia": 968.43,
  "pasos": [
    {
      "indice": 1,                   // número de iteración
      "probabilidades": [            // una entrada por ruta, todas visibles a la vez
        { "ruta": [0, 1, 2, 3, 4], "distancia": 1270.5, "probabilidad": 0.021 }
        // ... las 24
      ]
    }
    // ... una entrada por iteración
  ]
}
```

Manteniendo `pasos[].indice` y el campo `ruta` como lista de ids, el canvas
lee las dos respuestas con la misma lógica de dibujo — y el contador de la UI
solo cambia de etiqueta: *rutas evaluadas* en clásico, *iteraciones* en cuántico.

### Sobre el escenario de ruta cerrada

El enunciado no dice que el dron regrese a la base, así que el default es
**ruta abierta** (`cerrada: false`). El regreso está implementado como un flag
opcional, y vale la pena conocerlo porque **cambia el ganador, no solo la
distancia**:

| Escenario (semilla 42) | Mejor ruta | Distancia |
|---|---|---|
| Abierta (`cerrada: false`) | `[0, 4, 1, 2, 3]` | 968.43 |
| Cerrada (`cerrada: true`) | `[0, 3, 2, 1, 4]` | 1142.85 |

Si la Parte 2 implementa el mismo flag, es buen material para la presentación.

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
