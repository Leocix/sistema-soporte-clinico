# Panel médico — CDSS Adherencia

Frontend React + Vite del sistema de soporte clínico. Consume el API Gateway
de `backend-api/` y cubre el acceso del personal clínico (RF01), la gestión de
pacientes polimedicados (RF02) y la auditoría de adherencia (RF03, RF07).

## Cómo ejecutar

```bash
npm install
```

Copia `.env.example` como `.env` y ajusta `VITE_API_URL` si el API no está en
`http://127.0.0.1:8000`. Luego:

```bash
npm run dev
```

Necesitas el API corriendo en paralelo (`python run.py` desde `backend-api/`).

## Construcción para producción

```bash
npm run build
```

`VITE_API_URL` se incrusta en el paquete durante la construcción, no se lee en
tiempo de ejecución: si cambia, hay que volver a construir.

## Estructura

```
src/
├── App.jsx              # Enrutador
├── assets/estilos.css   # Guía de estilo del panel
├── components/          # Layout, AlertaRiesgo, FormularioPaciente, RutaProtegida
├── context/             # Sesión: contexto, proveedor y hook (archivos separados)
├── pages/               # LoginMedico, Dashboard, DetallePaciente
└── services/            # api (axios + JWT), riesgo (heurística), etiquetas
```

## Nota sobre la clasificación de riesgo

`services/riesgo.js` clasifica el riesgo a partir de la adherencia **ya
observada**, no con el modelo predictivo. Es una heurística provisional que
permite ordenar el panel por prioridad clínica hasta que el microservicio de
inferencia (RF04) y la explicabilidad SHAP (RF06) estén desplegados en el
Sprint 3.
