# Simulación de rutas de entrega — Clásico vs Cuántico (mini TSP)

Un "dron"/auto de entrega debe visitar 4 o 5 puntos siguiendo la ruta más
corta posible, comparando cómo se vería resuelto con computación clásica
(fuerza bruta) vs. una simulación visual de computación cuántica
(amplificación de probabilidad).

## Arquitectura

```
proyecto-tsp/
├── backend/                     Python (FastAPI). Puerto 8000.
│   ├── app.py                    Orquesta: arma la app y el endpoint /api/rutas
│   ├── comun/geometria.py        Compartido: cuadrícula, puntos, distancias
│   │                             y el cálculo de TODAS las rutas posibles
│   ├── clasico/logica_clasica.py Lógica del modo CLÁSICO (fuerza bruta)
│   ├── cuantica/logica_cuantica.py Lógica del modo CUÁNTICO (simulado)
│   └── requirements.txt
│
└── frontend/                    Next.js (React + TypeScript + Tailwind). Puerto 3000.
    ├── app/page.tsx              ★ LA VISTA/PÁGINA PRINCIPAL (ruta "/")
    ├── app/layout.tsx            Layout raíz de Next.js
    ├── Mapa/                     Todo lo que dibuja el mapa:
    │   ├── CityMap.tsx            componente visual (SVG) del mapa
    │   └── geometria.ts           conversión de coordenadas a píxeles/trazos
    ├── components/Controles.tsx  Botones (4/5 rutas, Clásico/Cuántico) y contador
    ├── hooks/useSimulacion.ts    El "cerebro": trae datos y anima con setInterval
    ├── Auxiliares/                Librerías auxiliares (no visuales):
    │   ├── tipos.ts               tipos compartidos (Punto, Ruta, Escenario...)
    │   └── api.ts                 llamada al backend + helper factorial
    └── (eslint.config.mjs, next.config.ts, postcss.config.mjs, tsconfig.json,
        next-env.d.ts, package.json) — configuración de las herramientas
        (Next.js, TypeScript, ESLint, PostCSS). Estos SIEMPRE deben quedarse
        en la raíz de "frontend/", porque cada herramienta los busca ahí
        automáticamente; moverlos rompería el proyecto.
```

El frontend le pide al backend un escenario (`GET /api/rutas?n=4`). El
backend calcula todas las rutas posibles (`comun/geometria.py`) y arma el
orden exacto en que se deben animar: aleatorio para el modo clásico
(`clasico/logica_clasica.py`), rondas de eliminación para el modo
cuántico (`cuantica/logica_cuantica.py`). El frontend reproduce ese guion
con `setInterval`.

El modo cuántico es una simulación visual: no usa ninguna librería de
computación cuántica real, solo imita el concepto de "amplificación de
amplitud" desvaneciendo progresivamente las rutas peores hasta que solo
queda la mejor, en pocas rondas (4 a 8).

## Cómo correrlo

Requisitos: Python 3.10+ y Node.js (LTS).

```bash
# Backend (dejar corriendo en una terminal)
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

```bash
# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

Abrir **http://localhost:3000**.

Si `uvicorn` no se reconoce como comando, usar `python -m uvicorn app:app --reload --port 8000`, o directamente `python app.py`.

## Qué hace cada botón

- **4 Rutas / 5 Rutas**: elige cuántos puntos de entrega tendrá el mapa
  (el punto 1 siempre es el depósito/inicio).
- **Clásico**: prueba las rutas una por una, en orden aleatorio (fuerza
  bruta), pintándolas en rojo, hasta terminar de revisarlas todas. Al
  final resalta en verde la más corta. Contador de "Intentos".
- **Cuántico (simulado)**: muestra todas las rutas posibles a la vez,
  semi-transparentes y parpadeando ("superposición"). Cada ronda elimina
  las rutas con peor distancia entre las que quedan, hasta que sobrevive
  una sola: la más corta, que se resalta en verde. Converge en pocas
  rondas (4 a 8), simulando ser más rápido que el modo clásico. Contador
  de "Iteraciones".
- **↻ Reiniciar**: vuelve a correr la simulación desde cero, con la misma
  configuración (número de rutas y modo) pero puntos y animación nuevos.
