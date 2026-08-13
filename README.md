# Ruta-de-entrega-mediante-computacion-cuantica-y-clasica
Se desarollara un programa que simule una ruta de entrega mediante computacion cuantica en un mapa tipo maps.

Stack tecnologico:
Logica: Python
Lenguaje del Framework: Typescript
Framework: Next.js

Caso 3. Ruta óptima de entrega (mini TSP, 4 a 5 puntos)
Problemática
Un dron de entrega debe visitar 4 o 5 puntos siguiendo la ruta más corta posible.
Mecanismo cuántico
A — Amplificación de probabilidad (aplicada a rutas en vez de casillas)
Entrada del programa
Coordenadas de 4-5 puntos en un canvas (fijas o generadas al azar al reiniciar).
Salida esperada
La ruta más corta encontrada por cada modo y cuántos caminos evaluó cada uno.


Parte 1 — Simulación clásica (bit)
Calcular todas las permutaciones posibles de los puntos (para 5 puntos son 4! = 24 rutas, fijando el punto de partida).
Dibujar cada ruta una por una sobre el mapa, calculando su distancia total, y llevar un contador de rutas evaluadas.
Al terminar, resaltar la ruta de menor distancia total encontrada.

Parte 2 — Simulación cuántica (qubit)
Generar el mismo conjunto de rutas posibles (las mismas permutaciones) pero dibujarlas todas a la vez, semi-transparentes, sobre el mismo mapa — esto representa la superposición.
Asignar a cada ruta una probabilidad inicial igual (1/total de rutas).
En cada iteración, aplicar el Mecanismo A: subir la probabilidad de la ruta más corta (la que cumple la condición) y bajar la de las demás; reflejar esto visualmente bajando la opacidad de las rutas menos probables en cada paso, hasta que solo quede una brillante.
Medir al final con la función ponderada y resaltar la ruta resultante como la elegida.
Elementos visuales obligatorios
Mapa o canvas con los puntos y líneas de ruta dibujadas.
En modo clásico: una sola ruta visible a la vez, cambiando en cada intento.
En modo cuántico: todas las rutas visibles a la vez, desvaneciéndose las malas iteración a iteración.
Contador de rutas evaluadas (clásico) vs. iteraciones (cuántico).
