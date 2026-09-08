# Exposición del producto acreditable al 50 %

`Exposicion_50.pptx` — 14 diapositivas, 16:9, con notas del orador en todas.

## Recorrido

Las láminas siguen el **orden de la lista de cotejo**, no el de los requisitos:
el evaluador recorre la rúbrica del ítem 1 al 20 y la baraja avanza con él. Cada
lámina lleva marcada arriba a la derecha la dimensión y los ítems que evidencia.

| # | Lámina | Dimensión · ítems |
| :---: | :--- | :--- |
| 1 | Portada | — |
| 2 | Hoja de ruta de la lista de cotejo | — |
| 3 | El seguimiento se hacía de memoria | 1 · ítem 1 |
| 4 | El escenario evaluado: el ciclo de una dosis | 1 · ítems 1-2 |
| 5 | La toma deja de tener una sola fuente | 1 · ítems 2-3 |
| 6 | Product Backlog | 1 · ítems 1-3 |
| 7 | Una aplicación pensada para un adulto mayor | 2 · ítems 4-6 |
| 8 | Lo que sostiene cada afirmación | 3 · ítems 7-8 |
| 9 | La toma se registra aunque no haya internet | 3 · ítems 8-9 |
| 10 | El sistema mide su propio tiempo de respuesta | 4 · ítems 10-11 |
| 11 | El rol no basta para autorizar | 5 · ítems 12-14 |
| 12 | Datos protegidos, operaciones impedidas | 5 · ítems 13-14 |
| 13 | Cinco componentes, todos ejecutables | 6 · ítems 15-16 |
| 14 | Scrum con CRISP-DM dentro | 6 · ítem 17 |
| 15 | El modelo vive dentro del sistema | 7 · ítems 18-20 |
| 16 | Estado de los objetivos específicos | — |
| 17 | Al corte del 50 % | — |

Todas llevan notas del orador. El guion paso a paso de la sustentación —qué
lámina, qué programa y qué decir en cada momento— se entrega aparte.

## Regenerar

La primera vez hay que instalar la dependencia; el generador la necesita y no
viene con el repositorio:

```bash
cd documentacion/04_exposicion
npm install
npm run build
```

Después basta con `npm run build`. Si al ejecutarlo aparece
`Cannot find module 'pptxgenjs'`, es que falta el `npm install` de la primera
línea, o que se está ejecutando desde otra carpeta: el generador resuelve la
dependencia desde el directorio en el que vive.

**Cierre el `.pptx` en PowerPoint antes de regenerar.** Windows bloquea el
archivo mientras está abierto y la escritura falla con «recurso ocupado».

El `.pptx` se produce desde el script: si lo edita a mano, la siguiente
ejecución sobrescribe los cambios. Para retoques puntuales de última hora,
edite el `.pptx` y no vuelva a ejecutar el generador.

Las cifras del guion —115 pruebas, 13 incidencias, 7 de 10 requisitos— proceden
del pre informe final y deben actualizarse a la vez que él.

## Requisitos

Node 18 o superior y `pptxgenjs` 4.0.1, fijado en `package.json`. `node_modules`
no se versiona.
