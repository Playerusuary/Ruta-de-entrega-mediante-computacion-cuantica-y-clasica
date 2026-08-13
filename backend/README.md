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
python3 -m unittest discover -s tests -v
```

## Estructura

| Archivo | Dueño | Qué hace |
|---|---|---|
| `app/geometria.py` | **compartido** | `Punto`, distancia euclidiana, longitud de ruta, generación de permutaciones y de mapas. |
| `app/esquemas.py` | **compartido** | Contrato de la API (modelos Pydantic). |
| `app/clasico.py` | Parte 1 (bit) | Fuerza bruta: evalúa las rutas una por una. |
| `app/main.py` | compartido | App FastAPI, CORS y endpoints. |

> `geometria.py` y `esquemas.py` los usan **las dos partes**. Si la simulación
> clásica y la cuántica miden las rutas distinto, la comparación final no
> significa nada. Cambios ahí se acuerdan entre ambos.

## Endpoints

### `GET /api/v1/puntos`

Genera el mapa de destinos.

| Param | Default | Nota |
|---|---|---|
| `n` | 5 | 2–8 destinos |
| `ancho` / `alto` | 800 / 600 | tamaño del canvas |
| `semilla` | — | fija el mapa; **con la misma semilla los dos modos corren sobre los mismos puntos** |

El primer punto (`id: 0`, etiqueta `Base`) es la base y queda fijo.

### `POST /api/v1/clasico/simular`

```jsonc
// request
{
  "puntos": [ { "id": 0, "x": 494.81, "y": 72.01, "etiqueta": "Base" }, /* ... */ ],
  "cerrada": false   // true = el dron regresa a la base (escenario opcional)
}
```

```jsonc
// response
{
  "modo": "clasico",
  "total_rutas": 24,          // (n-1)! con la base fija
  "rutas_evaluadas": 24,
  "mejor_ruta": [0, 4, 1, 2, 3],
  "mejor_distancia": 968.43,
  "pasos": [                  // la traza completa, en orden de evaluación
    {
      "indice": 1,                     // contador de rutas evaluadas
      "ruta": [0, 1, 2, 3, 4],
      "distancia": 1270.5,
      "es_mejor": true,                // rompió el récord → resaltar este frame
      "mejor_ruta": [0, 1, 2, 3, 4],   // campeona vigente tras este paso
      "mejor_distancia": 1270.5
    }
    // ... 23 más
  ]
}
```

**Por qué la traza completa en una sola llamada:** el frontend recibe los 24
pasos ya ordenados y los reproduce al ritmo que quiera. El servidor no guarda
estado entre frames y no hay un round-trip de red por cada ruta dibujada — el
tempo de la animación es decisión del front.

## Notas de diseño

**El módulo clásico no se optimiza.** Nada de vecino más cercano, programación
dinámica ni poda por cota. Es el grupo de control: si se vuelve listo, deja de
medir lo que la comparación contra el modo cuántico necesita medir. Su trabajo
es ser exhaustivo, no rápido.

**Ruta abierta por default.** El enunciado no dice que el dron regrese, así que
`cerrada: false`. El escenario de regreso está implementado y es un flag —
cambia el ganador, no solo la distancia: con la semilla 42, abierta gana
`[0,4,1,2,3]` (968.43) y cerrada gana `[0,3,2,1,4]` (1142.85).
