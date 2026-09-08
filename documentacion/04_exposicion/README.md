# Exposición del producto acreditable al 50 %

`Exposicion_50.pptx` — 14 diapositivas, 16:9, con notas del orador en todas.

## Recorrido

| # | Diapositiva | Qué evidencia |
| :---: | :--- | :--- |
| 1 | Portada | Identificación, plataforma y metodología |
| 2 | El problema | Diagnóstico (OE1) y las cuatro brechas |
| 3 | El escenario evaluado | El ciclo de una dosis, de inicio a fin |
| 4 | Scrum con CRISP-DM dentro | Metodología y estado de los cuatro sprints |
| 5 | Product Backlog | Los diez requisitos y su estado |
| 6 | Arquitectura y despliegue | Cinco componentes y verificación de seguridad |
| 7 | RF01 · RF02 | Acceso por perfil y reglas clínicas del alta |
| 8 | RF03 | Registro sin conexión e idempotencia |
| 9 | RF08 · RNF03 | Alertas en el dispositivo y navegación |
| 10 | RF09 | Grupo familiar: la toma con dos testigos |
| 11 | RF04 | El componente de IA integrado |
| 12 | Evidencia de calidad | 115 pruebas y registro de incidencias |
| 13 | Objetivos específicos | Avance de OE1 a OE5 |
| 14 | Cierre | Entregado frente a pendiente |

## Regenerar

```bash
cd documentacion/04_exposicion
npm install pptxgenjs
node generar_diapositivas.js
```

El `.pptx` se regenera desde el script; si lo editas a mano, la siguiente
ejecución sobrescribe los cambios. Para retoques puntuales antes de exponer,
edita el `.pptx` y no vuelvas a ejecutar el generador.

Las cifras del guion —115 pruebas, 13 incidencias, 7 de 10 requisitos— proceden
del pre informe final y deben actualizarse a la vez que él.
