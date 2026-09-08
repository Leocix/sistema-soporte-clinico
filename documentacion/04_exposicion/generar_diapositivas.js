/**
 * Diapositivas de exposición del producto acreditable al 50 %.
 *
 * Sistema de soporte clínico con aprendizaje automático — USAT 2026-II.
 * Leonardo Guzmán Salazar.
 */
const pptxgen = require("pptxgenjs");

// --- Paleta -----------------------------------------------------------------
// Azul petróleo profundo como color dominante, el azul del propio sistema como
// apoyo y un terracota cálido para lo que exige atención clínica. El verde y el
// rojo quedan reservados a su significado: cumplido y riesgo.
const C = {
  petroleo: "0F3D56",
  petroleoAlt: "17394C",
  azul: "17608F",
  azulClaro: "DCE9F2",
  coral: "C4552F",
  coralSuave: "FAE7DF",
  verde: "12704A",
  verdeSuave: "E1F0E9",
  ambar: "8A5B06",
  ambarSuave: "FBF1DE",
  tinta: "10212B",
  tintaSuave: "51636E",
  tintaTenue: "8496A2",
  fondo: "F4F7FA",
  blanco: "FFFFFF",
  linea: "D5DEE7",
};

const TITULO = "Cambria";
const CUERPO = "Calibri";

const W = 13.333;
const H = 7.5;
const M = 0.62; // margen lateral
const ANCHO = W - 2 * M;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Leonardo Jesús Guzmán Salazar";
pres.title = "Sistema de soporte clínico — avance al 50 %";

// --- Utilidades -------------------------------------------------------------

/** Lámina clara, con el título arriba y el número de lámina al pie. */
function lamina(titulo, entradilla) {
  const s = pres.addSlide();
  s.background = { color: C.fondo };

  s.addText(titulo, {
    x: M, y: 0.42, w: ANCHO, h: 0.62,
    fontFace: TITULO, fontSize: 30, bold: true, color: C.petroleo,
    align: "left", margin: 0, isTextBox: true,
  });

  if (entradilla) {
    s.addText(entradilla, {
      x: M, y: 1.06, w: ANCHO - 1.2, h: 0.42,
      fontFace: CUERPO, fontSize: 14, color: C.tintaSuave,
      align: "left", margin: 0, isTextBox: true,
    });
  }
  return s;
}

/** Lámina oscura: portada, secciones y cierre. */
function laminaOscura() {
  const s = pres.addSlide();
  s.background = { color: C.petroleo };
  return s;
}

/** Distintivo circular con el código del requisito. Es el motivo que se repite:
 *  cada funcionalidad aparece siempre junto al requisito del que procede. */
function distintivo(s, texto, x, y, opciones = {}) {
  const d = opciones.diametro || 0.62;
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: d, h: d,
    fill: { color: opciones.fondo || C.azul },
    line: { color: opciones.fondo || C.azul, width: 0 },
  });
  s.addText(texto, {
    x, y, w: d, h: d,
    fontFace: CUERPO, fontSize: opciones.tamano || 11, bold: true,
    color: opciones.color || C.blanco,
    align: "center", valign: "middle", margin: 0, isTextBox: true,
  });
}

/** Tarjeta blanca con sombra suave. */
function tarjeta(s, x, y, w, h, opciones = {}) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.06,
    fill: { color: opciones.fondo || C.blanco },
    line: { color: opciones.borde || C.linea, width: 1 },
    shadow: { type: "outer", color: "8FA3B0", blur: 6, offset: 1, angle: 90, opacity: 0.18 },
  });
}

function pie(s, texto) {
  s.addText(texto, {
    x: M, y: H - 0.52, w: ANCHO, h: 0.3,
    fontFace: CUERPO, fontSize: 10, color: C.tintaTenue,
    align: "left", margin: 0, isTextBox: true,
  });
}

// ===========================================================================
// 1 · Portada
// ===========================================================================
{
  const s = laminaOscura();

  s.addShape(pres.ShapeType.rect, {
    x: 0, y: 0, w: 4.6, h: H, fill: { color: C.petroleoAlt }, line: { width: 0 },
  });

  s.addText("USAT · Seminario de Tesis I", {
    x: 0.7, y: 0.85, w: 3.4, h: 0.3,
    fontFace: CUERPO, fontSize: 12, bold: true, color: C.azulClaro,
    charSpacing: 1.2, margin: 0, isTextBox: true,
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: 0.7, y: 1.45, w: 2.35, h: 0.5, rectRadius: 0.25,
    fill: { color: C.coral }, line: { width: 0 },
  });
  s.addText("HITO 2 · 50 %", {
    x: 0.7, y: 1.45, w: 2.35, h: 0.5,
    fontFace: CUERPO, fontSize: 13, bold: true, color: C.blanco,
    align: "center", valign: "middle", margin: 0, isTextBox: true,
  });

  s.addText("Leonardo Jesús\nGuzmán Salazar", {
    x: 0.7, y: 5.1, w: 3.4, h: 0.8,
    fontFace: TITULO, fontSize: 17, bold: true, color: C.blanco,
    lineSpacingMultiple: 1.05, margin: 0, isTextBox: true,
  });
  s.addText("Escuela de Ingeniería de Sistemas y Computación\nChiclayo · 08 de septiembre de 2026", {
    x: 0.7, y: 5.95, w: 3.4, h: 0.7,
    fontFace: CUERPO, fontSize: 11, color: C.azulClaro,
    lineSpacingMultiple: 1.2, margin: 0, isTextBox: true,
  });

  s.addText("Sistema de soporte clínico con aprendizaje automático", {
    x: 5.2, y: 1.85, w: 7.5, h: 1.9,
    fontFace: TITULO, fontSize: 34, bold: true, color: C.blanco,
    lineSpacingMultiple: 1.06, margin: 0, isTextBox: true,
  });
  s.addText(
    "Prevención del incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio médico Milko Ugaz Zegarra",
    {
      x: 5.2, y: 3.85, w: 7.2, h: 1.1,
      fontFace: CUERPO, fontSize: 14, color: C.azulClaro,
      lineSpacingMultiple: 1.25, margin: 0, isTextBox: true,
    },
  );

  const cifras = [
    ["7 / 10", "requisitos operativos"],
    ["115", "pruebas en verde"],
    ["3", "componentes desplegados"],
  ];
  cifras.forEach(([n, t], i) => {
    const x = 5.2 + i * 2.5;
    s.addText(n, {
      x, y: 5.35, w: 2.3, h: 0.55,
      fontFace: TITULO, fontSize: 26, bold: true, color: C.coral,
      margin: 0, isTextBox: true,
    });
    s.addText(t, {
      x, y: 5.92, w: 2.3, h: 0.5,
      fontFace: CUERPO, fontSize: 11, color: C.azulClaro,
      margin: 0, isTextBox: true,
    });
  });

  s.addNotes(
    "Presentación del avance al 50 % del producto acreditable. El sistema está " +
    "desplegado y es accesible: API en Render, panel en Vercel, base en Aiven y " +
    "un APK instalable. Siete de los diez requisitos funcionales operan de " +
    "extremo a extremo.",
  );
}

// ===========================================================================
// 2 · El problema
// ===========================================================================
{
  const s = lamina(
    "El seguimiento se hacía de memoria",
    "Diagnóstico del consultorio (OE1): entrevista semiestructurada al médico internista responsable.",
  );

  s.addText(
    "El cumplimiento se conocía por autorreporte verbal en consulta. Entre una cita y la siguiente no quedaba ningún registro, y el incumplimiento se detectaba cuando el paciente ya estaba descompensado.",
    {
      x: M, y: 1.62, w: 5.0, h: 1.5,
      fontFace: CUERPO, fontSize: 15, color: C.tinta,
      lineSpacingMultiple: 1.3, margin: 0, isTextBox: true,
    },
  );

  tarjeta(s, M, 3.35, 5.0, 1.5, { fondo: C.ambarSuave, borde: "E8D5AC" });
  s.addText("≈ 50 pacientes polimedicados", {
    x: M + 0.3, y: 3.58, w: 4.4, h: 0.35,
    fontFace: TITULO, fontSize: 17, bold: true, color: C.ambar,
    margin: 0, isTextBox: true,
  });
  s.addText(
    "con hipertensión, diabetes tipo 2 o ambas, y cinco o más fármacos simultáneos.",
    {
      x: M + 0.3, y: 3.98, w: 4.4, h: 0.7,
      fontFace: CUERPO, fontSize: 12.5, color: C.tinta,
      lineSpacingMultiple: 1.2, margin: 0, isTextBox: true,
    },
  );

  const brechas = [
    ["B1", "Sin registro estructurado", "El consumo real no queda documentado en ninguna parte."],
    ["B2", "Sin trazabilidad entre citas", "El médico no sabe qué ocurrió durante los tres meses previos."],
    ["B3", "Sin analítica predictiva", "No hay forma de anticipar quién va a incumplir."],
    ["B4", "Sin alertas ni recordatorios", "Ni el paciente recibe avisos ni el médico señales tempranas."],
  ];
  brechas.forEach(([cod, tit, txt], i) => {
    const x = 6.05 + (i % 2) * 3.42;
    const y = 1.62 + Math.floor(i / 2) * 1.72;
    tarjeta(s, x, y, 3.22, 1.46);
    distintivo(s, cod, x + 0.22, y + 0.2, { diametro: 0.52, tamano: 12, fondo: C.coral });
    s.addText(tit, {
      x: x + 0.86, y: y + 0.14, w: 2.18, h: 0.5,
      fontFace: CUERPO, fontSize: 12.5, bold: true, color: C.petroleo,
      valign: "middle", lineSpacingMultiple: 1.05, margin: 0, isTextBox: true,
    });
    s.addText(txt, {
      x: x + 0.22, y: y + 0.7, w: 2.82, h: 0.7,
      fontFace: CUERPO, fontSize: 11, color: C.tintaSuave,
      lineSpacingMultiple: 1.16, margin: 0, isTextBox: true,
    });
  });

  pie(s, "Cada brecha se tradujo en un requisito funcional. La trazabilidad brecha → requisito → archivo → prueba está documentada.");
  s.addNotes(
    "Las cuatro brechas salen de la entrevista, no de una intuición. Cada una " +
    "está trazada a un requisito funcional concreto, y ese requisito al archivo " +
    "que lo implementa y a la prueba que lo verifica.",
  );
}

// ===========================================================================
// 3 · El escenario evaluado
// ===========================================================================
{
  const s = lamina(
    "El escenario evaluado: el ciclo de una dosis",
    "Es la funcionalidad principal que se demuestra de inicio a fin.",
  );

  const pasos = [
    ["1", "Alta del paciente", "Panel web", "El médico registra la ficha con las variables del Anexo n.º 04 y sus reglas clínicas.", C.azul],
    ["2", "Registro de la toma", "App móvil", "El paciente confirma cada dosis. Sin conexión queda en cola y se envía al reconectar.", C.azul],
    ["3", "Corroboración", "App del familiar", "Un conviviente da fe de la toma. El evento pasa a tener dos fuentes.", C.coral],
    ["4", "Predicción de riesgo", "Modelo + panel", "El sistema estima la probabilidad de incumplimiento antes del próximo control.", C.verde],
  ];

  pasos.forEach(([n, tit, comp, txt, color], i) => {
    const x = M + i * 3.13;
    tarjeta(s, x, 1.78, 2.86, 3.3);
    distintivo(s, n, x + 1.13, 2.02, { diametro: 0.6, tamano: 15, fondo: color });
    s.addText(tit, {
      x: x + 0.18, y: 2.78, w: 2.5, h: 0.36,
      fontFace: TITULO, fontSize: 15, bold: true, color: C.petroleo,
      align: "center", margin: 0, isTextBox: true,
    });
    s.addText(comp, {
      x: x + 0.18, y: 3.16, w: 2.5, h: 0.28,
      fontFace: CUERPO, fontSize: 11, bold: true, color,
      align: "center", charSpacing: 0.6, margin: 0, isTextBox: true,
    });
    s.addText(txt, {
      x: x + 0.24, y: 3.56, w: 2.38, h: 1.35,
      fontFace: CUERPO, fontSize: 11.5, color: C.tintaSuave,
      align: "center", lineSpacingMultiple: 1.2, margin: 0, isTextBox: true,
    });

    if (i < 3) {
      s.addShape(pres.ShapeType.rightArrow, {
        x: x + 2.92, y: 3.28, w: 0.16, h: 0.24,
        fill: { color: C.tintaTenue }, line: { width: 0 },
      });
    }
  });

  tarjeta(s, M, 5.36, ANCHO, 1.02, { fondo: C.azulClaro, borde: "BBD3E4" });
  s.addText(
    "El ciclo completo se recorre sobre la infraestructura desplegada, no en un entorno local: base de datos en Aiven, API en Render, panel en Vercel y la aplicación instalada desde un APK de publicación.",
    {
      x: M + 0.3, y: 5.55, w: ANCHO - 0.6, h: 0.68,
      fontFace: CUERPO, fontSize: 13, color: C.petroleo,
      lineSpacingMultiple: 1.2, margin: 0, isTextBox: true,
    },
  );
  s.addNotes(
    "Este es el escenario que evalúa la lista de cotejo. No se eligió por " +
    "comodidad: recorre las cuatro brechas del diagnóstico en orden.",
  );
}

// ===========================================================================
// 4 · Metodología
// ===========================================================================
{
  const s = lamina(
    "Scrum con CRISP-DM dentro",
    "La unidad de trabajo es el sprint. Las fases de CRISP-DM no corren en paralelo: se ejecutan dentro de él.",
  );

  s.addText(
    "Un sprint que solo entregara código dejaría al modelo sin datos que aprender; uno que solo entregara analítica no produciría el software que captura esos datos.",
    {
      x: M, y: 1.72, w: 4.55, h: 1.15,
      fontFace: CUERPO, fontSize: 14, color: C.tinta,
      lineSpacingMultiple: 1.28, margin: 0, isTextBox: true,
    },
  );
  s.addText(
    "Al exigir que cada sprint cierre ambos frentes, la traza digital que genera el sistema alimenta el dataset del sprint siguiente, y lo aprendido del dataset redefine lo que el software debe capturar.",
    {
      x: M, y: 2.98, w: 4.55, h: 1.4,
      fontFace: CUERPO, fontSize: 13, color: C.tintaSuave,
      lineSpacingMultiple: 1.28, margin: 0, isTextBox: true,
    },
  );

  tarjeta(s, M, 4.62, 4.55, 1.72, { fondo: C.verdeSuave, borde: "BFDECD" });
  s.addText("Artefactos vivos", {
    x: M + 0.28, y: 4.82, w: 4.0, h: 0.32,
    fontFace: CUERPO, fontSize: 13, bold: true, color: C.verde,
    margin: 0, isTextBox: true,
  });
  s.addText(
    [
      { text: "Product Backlog general priorizado con MoSCoW", options: { bullet: true, breakLine: true } },
      { text: "Sprint Backlog de cada uno de los cuatro sprints", options: { bullet: true, breakLine: true } },
      { text: "Registro de incidencias con causa raíz", options: { bullet: true } },
    ],
    {
      x: M + 0.28, y: 5.18, w: 4.05, h: 1.0,
      fontFace: CUERPO, fontSize: 11.5, color: C.tinta,
      paraSpaceAfter: 3, margin: 0, isTextBox: true,
    },
  );

  const filas = [
    ["1", "Planificación y primer incremento", "Business + Data Understanding", "2–3", "Cerrado", C.verde],
    ["2", "Núcleo funcional y modelado inicial", "Data Preparation + Modeling", "3–4", "Cerrado", C.verde],
    ["3", "Integración del modelo y complementos", "Modeling + Evaluation", "5–6", "En ejecución", C.coral],
    ["4", "Rendimiento y validación de usabilidad", "Deployment y monitoreo", "7–8", "Programado", C.tintaTenue],
  ];

  const tx = 5.55;
  s.addText("SPRINT", { x: tx + 0.16, y: 1.72, w: 0.72, h: 0.28, fontFace: CUERPO, fontSize: 9.5, bold: true, color: C.tintaTenue, charSpacing: 0.8, margin: 0, isTextBox: true });
  s.addText("OBJETIVO Y FASE CRISP-DM", { x: tx + 0.95, y: 1.72, w: 4.0, h: 0.28, fontFace: CUERPO, fontSize: 9.5, bold: true, color: C.tintaTenue, charSpacing: 0.8, margin: 0, isTextBox: true });
  s.addText("SEM.", { x: tx + 5.02, y: 1.72, w: 0.6, h: 0.28, fontFace: CUERPO, fontSize: 9.5, bold: true, color: C.tintaTenue, charSpacing: 0.8, margin: 0, isTextBox: true });
  s.addText("ESTADO", { x: tx + 5.66, y: 1.72, w: 1.3, h: 0.28, fontFace: CUERPO, fontSize: 9.5, bold: true, color: C.tintaTenue, charSpacing: 0.8, margin: 0, isTextBox: true });

  filas.forEach(([n, obj, fase, sem, est, color], i) => {
    const y = 2.1 + i * 1.16;
    tarjeta(s, tx, y, 7.1, 1.02);
    distintivo(s, n, tx + 0.2, y + 0.22, { diametro: 0.58, tamano: 15, fondo: C.petroleo });
    s.addText(obj, {
      x: tx + 0.95, y: y + 0.16, w: 4.0, h: 0.34,
      fontFace: CUERPO, fontSize: 12.5, bold: true, color: C.petroleo,
      margin: 0, isTextBox: true,
    });
    s.addText(fase, {
      x: tx + 0.95, y: y + 0.52, w: 4.0, h: 0.32,
      fontFace: CUERPO, fontSize: 11, italic: true, color: C.tintaSuave,
      margin: 0, isTextBox: true,
    });
    s.addText(sem, {
      x: tx + 4.98, y: y + 0.34, w: 0.62, h: 0.3,
      fontFace: CUERPO, fontSize: 12, color: C.tintaSuave,
      margin: 0, isTextBox: true,
    });
    s.addText(est, {
      x: tx + 5.66, y: y + 0.34, w: 1.3, h: 0.3,
      fontFace: CUERPO, fontSize: 11.5, bold: true, color,
      margin: 0, isTextBox: true,
    });
  });

  s.addNotes(
    "El Sprint 3 figura en ejecución y no programado porque parte de su alcance " +
    "se adelantó: el modelo ya está integrado en el sistema.",
  );
}

// ===========================================================================
// 5 · Product Backlog
// ===========================================================================
{
  const s = lamina(
    "Product Backlog: siete de diez operativos",
    "Priorizado con MoSCoW por dependencia respecto de la hipótesis, no por facilidad de implementación.",
  );

  const OK = "Operativo", PA = "Parcial", PE = "Pendiente";
  const reqs = [
    ["RF01", "Acceso y autorización por perfil", "Must", OK],
    ["RF02", "Gestión de pacientes polimedicados", "Must", OK],
    ["RF03", "Registro de la toma desde el móvil", "Must", OK],
    ["RF04", "Predicción del riesgo de incumplimiento", "Must", OK],
    ["RF05", "Alertas tempranas al médico", "Must", PE],
    ["RF06", "Explicabilidad de la predicción", "Should", PA],
    ["RF07", "Panel de auditoría con reportes", "Should", PA],
    ["RF08", "Recordatorios de toma al paciente", "Could", OK],
    ["RF09", "Corroboración por el grupo familiar", "Should", OK],
    ["RF10", "Restablecimiento de la contraseña", "Should", OK],
  ];

  const tono = { [OK]: [C.verde, C.verdeSuave], [PA]: [C.ambar, C.ambarSuave], [PE]: [C.tintaSuave, "EAEFF3"] };

  reqs.forEach(([cod, nom, pri, est], i) => {
    const x = M + (i % 2) * 6.28;
    const y = 1.72 + Math.floor(i / 2) * 0.94;
    tarjeta(s, x, y, 5.98, 0.8);
    const [colorEst, fondoEst] = tono[est];
    distintivo(s, cod, x + 0.16, y + 0.13, { diametro: 0.54, tamano: 9.5, fondo: C.petroleo });
    s.addText(nom, {
      x: x + 0.82, y: y + 0.24, w: 3.4, h: 0.34,
      fontFace: CUERPO, fontSize: 12.5, color: C.tinta,
      margin: 0, isTextBox: true,
    });
    s.addText(pri, {
      x: x + 4.2, y: y + 0.26, w: 0.72, h: 0.3,
      fontFace: CUERPO, fontSize: 10.5, italic: true, color: C.tintaTenue,
      margin: 0, isTextBox: true,
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: x + 4.92, y: y + 0.21, w: 0.9, h: 0.38, rectRadius: 0.19,
      fill: { color: fondoEst }, line: { width: 0 },
    });
    s.addText(est, {
      x: x + 4.92, y: y + 0.21, w: 0.9, h: 0.38,
      fontFace: CUERPO, fontSize: 9.5, bold: true, color: colorEst,
      align: "center", valign: "middle", margin: 0, isTextBox: true,
    });
  });

  pie(s, "RF09 y RF10 no estaban en la pila inicial: emergieron al inspeccionar el incremento, que es lo que Scrum prescribe para el Product Backlog.");
  s.addNotes(
    "RF09 nace al ver que la brecha B1 quedaba a medias: hay traza digital, pero " +
    "su única fuente sigue siendo el paciente. RF10 nace al ver que remitir al " +
    "consultorio por un olvido convierte el olvido en un viaje.",
  );
}

// ===========================================================================
// 6 · Arquitectura y despliegue
// ===========================================================================
{
  const s = lamina(
    "Cinco componentes, tres desplegados",
    "Arquitectura separada por responsabilidad, cada pieza desplegable de forma independiente.",
  );

  const comps = [
    ["API", "API Gateway", "FastAPI + PostgreSQL", "Render", C.azul],
    ["WEB", "Panel médico", "React + Vite", "Vercel", C.azul],
    ["APP", "App del paciente", "Flutter", "APK de publicación", C.coral],
    ["ML", "Pipeline CRISP-DM", "scikit-learn", "Artefacto versionado", C.verde],
    ["BD", "Base clínica", "PostgreSQL", "Aiven · TLS", C.petroleo],
  ];

  comps.forEach(([sig, nom, tec, dep, color], i) => {
    const x = M + i * 2.47;
    tarjeta(s, x, 1.82, 2.25, 2.55);
    distintivo(s, sig, x + 0.79, 2.08, { diametro: 0.68, tamano: 11, fondo: color });
    s.addText(nom, {
      x: x + 0.14, y: 2.94, w: 1.97, h: 0.34,
      fontFace: TITULO, fontSize: 13.5, bold: true, color: C.petroleo,
      align: "center", margin: 0, isTextBox: true,
    });
    s.addText(tec, {
      x: x + 0.14, y: 3.3, w: 1.97, h: 0.32,
      fontFace: CUERPO, fontSize: 11, color: C.tintaSuave,
      align: "center", margin: 0, isTextBox: true,
    });
    s.addText(dep, {
      x: x + 0.14, y: 3.72, w: 1.97, h: 0.5,
      fontFace: CUERPO, fontSize: 10.5, bold: true, color,
      align: "center", lineSpacingMultiple: 1.15, margin: 0, isTextBox: true,
    });
  });

  const verificado = [
    ["Documentación interactiva oculta", "404 en /docs"],
    ["Cabecera Host falsificada", "Rechazada con 403"],
    ["Conexión cifrada a la base clínica", "sslmode=require"],
    ["Cabeceras de seguridad", "HSTS · CSP · nosniff"],
  ];
  verificado.forEach(([txt, res], i) => {
    const x = M + (i % 2) * 6.28;
    const y = 4.72 + Math.floor(i / 2) * 0.86;
    tarjeta(s, x, y, 5.98, 0.76, { fondo: C.verdeSuave, borde: "BFDECD" });
    s.addText("✓", {
      x: x + 0.2, y: y + 0.18, w: 0.35, h: 0.4,
      fontFace: CUERPO, fontSize: 16, bold: true, color: C.verde,
      align: "center", margin: 0, isTextBox: true,
    });
    s.addText(txt, {
      x: x + 0.62, y: y + 0.14, w: 3.45, h: 0.48,
      fontFace: CUERPO, fontSize: 12, color: C.tinta,
      valign: "middle", lineSpacingMultiple: 1.05, margin: 0, isTextBox: true,
    });
    s.addText(res, {
      x: x + 4.1, y: y + 0.14, w: 1.7, h: 0.48,
      fontFace: CUERPO, fontSize: 11, bold: true, color: C.verde,
      align: "right", valign: "middle", margin: 0, isTextBox: true,
    });
  });

  s.addNotes(
    "Las cuatro comprobaciones se ejecutaron contra el dominio público, no en " +
    "local. Un 401 y no un 503 ante credenciales inválidas prueba además que la " +
    "conexión con la base funciona.",
  );
}

// ===========================================================================
// 7 · RF01 y RF02
// ===========================================================================
{
  const s = lamina(
    "El rol no basta para autorizar",
    "RF01 y RF02 · Acceso diferenciado y alta del paciente polimedicado.",
  );

  tarjeta(s, M, 1.78, 5.92, 4.5);
  distintivo(s, "RF01", M + 0.32, 2.02, { diametro: 0.62, tamano: 10, fondo: C.azul });
  s.addText("Acceso por perfil", {
    x: M + 1.08, y: 2.1, w: 4.4, h: 0.4,
    fontFace: TITULO, fontSize: 18, bold: true, color: C.petroleo,
    margin: 0, isTextBox: true,
  });
  s.addText(
    [
      { text: "Un paciente autenticado tiene rol válido, pero solo sobre su propia ficha.", options: { bullet: true, breakLine: true } },
      { text: "El médico accede únicamente a los pacientes que tiene a cargo como tratante.", options: { bullet: true, breakLine: true } },
      { text: "Credencial inexistente, contraseña incorrecta y perfil equivocado devuelven el mismo mensaje: no se pueden enumerar cuentas.", options: { bullet: true, breakLine: true } },
      { text: "La regla vive en un único módulo, para que ningún endpoint la olvide.", options: { bullet: true } },
    ],
    {
      x: M + 0.34, y: 2.72, w: 5.3, h: 3.3,
      fontFace: CUERPO, fontSize: 13, color: C.tinta,
      lineSpacingMultiple: 1.2, paraSpaceAfter: 9, margin: 0, isTextBox: true,
    },
  );

  tarjeta(s, 6.82, 1.78, 5.92, 4.5);
  distintivo(s, "RF02", 7.14, 2.02, { diametro: 0.62, tamano: 10, fondo: C.coral });
  s.addText("Reglas clínicas que rechazan el alta", {
    x: 7.9, y: 2.1, w: 4.7, h: 0.4,
    fontFace: TITULO, fontSize: 18, bold: true, color: C.petroleo,
    margin: 0, isTextBox: true,
  });

  const reglas = [
    ["≥ 5 fármacos", "Criterio de elegibilidad del estudio: sin polimedicación, el paciente no entra."],
    ["Controles coherentes", "Los controles perdidos no pueden superar a los programados."],
    ["Edad y Morisky en rango", "18–120 años; puntaje del test entre 0 y 4."],
  ];
  reglas.forEach(([tit, txt], i) => {
    const y = 2.78 + i * 1.12;
    s.addText(tit, {
      x: 7.16, y, w: 5.2, h: 0.32,
      fontFace: CUERPO, fontSize: 13, bold: true, color: C.coral,
      margin: 0, isTextBox: true,
    });
    s.addText(txt, {
      x: 7.16, y: y + 0.34, w: 5.2, h: 0.62,
      fontFace: CUERPO, fontSize: 12, color: C.tintaSuave,
      lineSpacingMultiple: 1.18, margin: 0, isTextBox: true,
    });
  });

  s.addText(
    "No son validaciones dispersas en la interfaz: son restricciones declarativas de la base de datos.",
    {
      x: 7.16, y: 5.72, w: 5.2, h: 0.44,
      fontFace: CUERPO, fontSize: 11.5, italic: true, color: C.petroleo,
      lineSpacingMultiple: 1.15, margin: 0, isTextBox: true,
    },
  );

  s.addNotes(
    "En la demostración se intenta el alta con cuatro fármacos: el sistema la " +
    "rechaza, explica el motivo y no borra lo ya escrito.",
  );
}

// ===========================================================================
// 8 · RF03
// ===========================================================================
{
  const s = lamina(
    "La toma se registra aunque no haya internet",
    "RF03 · El escenario para el que se diseñó la aplicación, no una excepción.",
  );

  const flujo = [
    ["Sin cobertura", "El paciente confirma la dosis y el evento queda guardado en el teléfono.", C.ambar, C.ambarSuave],
    ["Al reconectar", "La cola se envía en un solo lote, dentro de una única transacción.", C.azul, C.azulClaro],
    ["Si el envío se repite", "El evento se actualiza, no se duplica: la terna paciente, medicamento y horario lo identifica.", C.verde, C.verdeSuave],
  ];

  flujo.forEach(([tit, txt, color, fondo], i) => {
    const x = M + i * 4.18;
    tarjeta(s, x, 1.85, 3.86, 2.25, { fondo, borde: fondo });
    s.addText(tit, {
      x: x + 0.28, y: 2.08, w: 3.3, h: 0.36,
      fontFace: TITULO, fontSize: 16, bold: true, color,
      margin: 0, isTextBox: true,
    });
    s.addText(txt, {
      x: x + 0.28, y: 2.52, w: 3.3, h: 1.34,
      fontFace: CUERPO, fontSize: 12.5, color: C.tinta,
      lineSpacingMultiple: 1.24, margin: 0, isTextBox: true,
    });
    if (i < 2) {
      s.addShape(pres.ShapeType.rightArrow, {
        x: x + 3.94, y: 2.86, w: 0.16, h: 0.24,
        fill: { color: C.tintaTenue }, line: { width: 0 },
      });
    }
  });

  tarjeta(s, M, 4.42, ANCHO, 1.92);
  s.addText("Por qué la idempotencia importa a la investigación", {
    x: M + 0.34, y: 4.66, w: 11.5, h: 0.36,
    fontFace: TITULO, fontSize: 16, bold: true, color: C.petroleo,
    margin: 0, isTextBox: true,
  });
  s.addText(
    "Un reintento que duplicara el evento inflaría la tasa de adherencia observada, y esa tasa es la variable conductual que alimenta al modelo predictivo. La protección no es una comodidad de la aplicación: es lo que sostiene la validez del dataset.",
    {
      x: M + 0.34, y: 5.1, w: 11.4, h: 1.02,
      fontFace: CUERPO, fontSize: 13, color: C.tinta,
      lineSpacingMultiple: 1.26, margin: 0, isTextBox: true,
    },
  );

  s.addNotes(
    "Buena parte de los pacientes del consultorio vive en zona rural con " +
    "cobertura intermitente. Una aplicación que exigiera conexión fallaría " +
    "justo con quien más la necesita.",
  );
}

// ===========================================================================
// 9 · RF08 y la app del paciente
// ===========================================================================
{
  const s = lamina(
    "Una aplicación pensada para un adulto mayor",
    "RF08 y RNF03 · Alertas en el dispositivo y navegación sin menús ocultos.",
  );

  tarjeta(s, M, 1.8, 5.92, 2.35);
  distintivo(s, "RF08", M + 0.32, 2.04, { diametro: 0.62, tamano: 10, fondo: C.coral });
  s.addText("Las alertas viven en el teléfono", {
    x: M + 1.08, y: 2.12, w: 4.5, h: 0.4,
    fontFace: TITULO, fontSize: 17, bold: true, color: C.petroleo,
    margin: 0, isTextBox: true,
  });
  s.addText(
    "No se envían desde el servidor. El paciente puede estar sin cobertura justo a la hora de su medicación, que es precisamente el momento en que más necesita el aviso. El permiso se pide al guardar el primer medicamento con su horario: el único instante en que la petición se explica sola.",
    {
      x: M + 0.34, y: 2.68, w: 5.3, h: 1.34,
      fontFace: CUERPO, fontSize: 12.5, color: C.tinta,
      lineSpacingMultiple: 1.24, margin: 0, isTextBox: true,
    },
  );

  tarjeta(s, M, 4.4, 5.92, 1.95, { fondo: C.azulClaro, borde: "BBD3E4" });
  s.addText("Cuatro destinos rotulados, siempre visibles", {
    x: M + 0.34, y: 4.62, w: 5.3, h: 0.34,
    fontFace: CUERPO, fontSize: 13, bold: true, color: C.petroleo,
    margin: 0, isTextBox: true,
  });
  ["Hoy", "Medicinas", "Familia", "Mi cuenta"].forEach((t, i) => {
    const x = M + 0.34 + i * 1.38;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 5.06, w: 1.24, h: 0.48, rectRadius: 0.08,
      fill: { color: C.blanco }, line: { color: "BBD3E4", width: 1 },
    });
    s.addText(t, {
      x, y: 5.06, w: 1.24, h: 0.48,
      fontFace: CUERPO, fontSize: 11, bold: true, color: C.azul,
      align: "center", valign: "middle", margin: 0, isTextBox: true,
    });
  });
  s.addText(
    "Un icono sin etiqueta en una esquina no es un menú para este usuario: es una función que no existe.",
    {
      x: M + 0.34, y: 5.66, w: 5.3, h: 0.46,
      fontFace: CUERPO, fontSize: 11.5, italic: true, color: C.tintaSuave,
      lineSpacingMultiple: 1.15, margin: 0, isTextBox: true,
    },
  );

  tarjeta(s, 6.82, 1.8, 5.92, 4.55, { fondo: C.coralSuave, borde: "EDCDBF" });
  s.addText("Un defecto que solo se ve en el artefacto que se entrega", {
    x: 7.14, y: 2.06, w: 5.3, h: 0.74,
    fontFace: TITULO, fontSize: 17, bold: true, color: C.coral,
    lineSpacingMultiple: 1.08, margin: 0, isTextBox: true,
  });
  s.addText(
    "El manifiesto de publicación de Android no declaraba el permiso de INTERNET. Las herramientas de Flutter lo añaden por su cuenta en los manifiestos de depuración y de perfil, que no se fusionan en la compilación de publicación.",
    {
      x: 7.14, y: 2.92, w: 5.3, h: 1.3,
      fontFace: CUERPO, fontSize: 12.5, color: C.tinta,
      lineSpacingMultiple: 1.24, margin: 0, isTextBox: true,
    },
  );
  s.addText(
    "Resultado: la aplicación funcionaba durante todo el desarrollo y quedaba permanentemente «sin conexión» al instalarse desde el APK.",
    {
      x: 7.14, y: 4.3, w: 5.3, h: 0.92,
      fontFace: CUERPO, fontSize: 12.5, bold: true, color: C.coral,
      lineSpacingMultiple: 1.24, margin: 0, isTextBox: true,
    },
  );
  s.addText(
    "De ahí una regla que ya forma parte del procedimiento de verificación: probar el APK de publicación, no solo la ejecución en depuración.",
    {
      x: 7.14, y: 5.32, w: 5.3, h: 0.86,
      fontFace: CUERPO, fontSize: 12, italic: true, color: C.tintaSuave,
      lineSpacingMultiple: 1.22, margin: 0, isTextBox: true,
    },
  );

  s.addNotes(
    "Este defecto está en el registro de incidencias como I-08. Es el mejor " +
    "ejemplo de por qué la verificación tiene que hacerse sobre el entregable.",
  );
}

// ===========================================================================
// 10 · RF09
// ===========================================================================
{
  const s = lamina(
    "La toma deja de tener una sola fuente",
    "RF09 · Grupo familiar de acompañamiento.",
  );

  tarjeta(s, M, 1.8, 5.5, 1.9, { fondo: "EAEFF3", borde: C.linea });
  s.addText("ANTES", {
    x: M + 0.32, y: 2.0, w: 2.0, h: 0.3,
    fontFace: CUERPO, fontSize: 10.5, bold: true, color: C.tintaTenue,
    charSpacing: 1.2, margin: 0, isTextBox: true,
  });
  s.addText("Una sola fuente", {
    x: M + 0.32, y: 2.32, w: 4.9, h: 0.4,
    fontFace: TITULO, fontSize: 19, bold: true, color: C.tintaSuave,
    margin: 0, isTextBox: true,
  });
  s.addText("El paciente marca su propia toma. Mejor que el recuerdo verbal, pero conserva su sesgo.", {
    x: M + 0.32, y: 2.78, w: 4.9, h: 0.76,
    fontFace: CUERPO, fontSize: 12.5, color: C.tintaSuave,
    lineSpacingMultiple: 1.2, margin: 0, isTextBox: true,
  });

  tarjeta(s, M, 3.98, 5.5, 2.38, { fondo: C.verdeSuave, borde: "BFDECD" });
  s.addText("DESPUÉS", {
    x: M + 0.32, y: 4.18, w: 2.0, h: 0.3,
    fontFace: CUERPO, fontSize: 10.5, bold: true, color: C.verde,
    charSpacing: 1.2, margin: 0, isTextBox: true,
  });
  s.addText("Dos testigos", {
    x: M + 0.32, y: 4.5, w: 4.9, h: 0.4,
    fontFace: TITULO, fontSize: 19, bold: true, color: C.verde,
    margin: 0, isTextBox: true,
  });
  s.addText(
    "Un conviviente corrobora la dosis desde su propio dispositivo. El historial del panel médico distingue, evento a evento, si la toma tiene dos fuentes o solo la palabra del paciente.",
    {
      x: M + 0.32, y: 4.96, w: 4.9, h: 1.24,
      fontFace: CUERPO, fontSize: 12.5, color: C.tinta,
      lineSpacingMultiple: 1.24, margin: 0, isTextBox: true,
    },
  );

  const reglas = [
    ["Solo el paciente invita, y solo él retira", "Es un consentimiento, no una vigilancia."],
    ["Código de un solo uso, vence a los 7 días", "Una invitación pendiente es una credencial de alta."],
    ["Solo se corroboran tomas cumplidas", "Una omisión ya es una declaración contra el propio interés."],
    ["La corroboración caduca a las 48 horas", "Quien da fe debe haber podido presenciarla."],
    ["El acompañante no ve la ficha ni registra tomas", "Corroborar no es reportar por otro."],
  ];
  s.addText("Cinco reglas, y ninguna sobra", {
    x: 6.44, y: 1.8, w: 6.3, h: 0.36,
    fontFace: TITULO, fontSize: 17, bold: true, color: C.petroleo,
    margin: 0, isTextBox: true,
  });
  reglas.forEach(([tit, txt], i) => {
    const y = 2.3 + i * 0.85;
    tarjeta(s, 6.44, y, 6.3, 0.74);
    s.addText(tit, {
      x: 6.68, y: y + 0.08, w: 5.9, h: 0.3,
      fontFace: CUERPO, fontSize: 12, bold: true, color: C.petroleo,
      margin: 0, isTextBox: true,
    });
    s.addText(txt, {
      x: 6.68, y: y + 0.38, w: 5.9, h: 0.3,
      fontFace: CUERPO, fontSize: 11, color: C.tintaSuave,
      margin: 0, isTextBox: true,
    });
  });

  s.addNotes(
    "La corroboración se añade al registro: no lo sustituye ni lo modifica. Eso " +
    "deja disponible, para el análisis posterior, una variable de calidad de la " +
    "evidencia por evento.",
  );
}

// ===========================================================================
// 11 · RF04 — el componente de IA
// ===========================================================================
{
  const s = lamina(
    "El modelo dentro del sistema, no en un cuaderno",
    "RF04 · Predicción del riesgo de incumplimiento antes del próximo control.",
  );

  tarjeta(s, M, 1.8, 4.15, 4.55);
  s.addText("RIESGO PREDICHO POR EL MODELO", {
    x: M + 0.3, y: 2.02, w: 3.6, h: 0.3,
    fontFace: CUERPO, fontSize: 9.5, bold: true, color: C.tintaTenue,
    charSpacing: 0.7, margin: 0, isTextBox: true,
  });
  s.addText("76 %", {
    x: M + 0.3, y: 2.38, w: 3.6, h: 1.0,
    fontFace: TITULO, fontSize: 60, bold: true, color: C.coral,
    margin: 0, isTextBox: true,
  });
  s.addText("de probabilidad de incumplimiento antes del próximo control", {
    x: M + 0.3, y: 3.42, w: 3.55, h: 0.66,
    fontFace: CUERPO, fontSize: 12, color: C.tinta,
    lineSpacingMultiple: 1.2, margin: 0, isTextBox: true,
  });

  s.addText("FACTORES QUE MÁS PESAN", {
    x: M + 0.3, y: 4.2, w: 3.6, h: 0.28,
    fontFace: CUERPO, fontSize: 9.5, bold: true, color: C.tintaTenue,
    charSpacing: 0.7, margin: 0, isTextBox: true,
  });
  const factores = [["Inasistencia a controles", 100], ["Carga terapéutica", 36], ["Número de fármacos", 14]];
  factores.forEach(([nom, pct], i) => {
    const y = 4.56 + i * 0.52;
    s.addText(nom, {
      x: M + 0.3, y, w: 2.2, h: 0.3,
      fontFace: CUERPO, fontSize: 11, color: C.tinta,
      margin: 0, isTextBox: true,
    });
    s.addShape(pres.ShapeType.rect, {
      x: M + 2.55, y: y + 0.09, w: 1.3, h: 0.14,
      fill: { color: "E4EAF0" }, line: { width: 0 },
    });
    s.addShape(pres.ShapeType.rect, {
      x: M + 2.55, y: y + 0.09, w: (1.3 * pct) / 100, h: 0.14,
      fill: { color: C.azul }, line: { width: 0 },
    });
  });

  const puntos = [
    ["Se carga una sola vez por proceso", "El pipeline serializado incluye su preprocesador: la transformación en producción es idéntica a la del entrenamiento."],
    ["Declara lo que tuvo que suponer", "La respuesta indica qué variables estaban ausentes en la ficha y el modelo hubo de imputar."],
    ["Su ausencia no tumba el sistema", "Si el artefacto no está disponible responde 503 y el resto de la ficha sigue funcionando."],
    ["No se presenta como diagnóstico", "La interfaz declara que es apoyo a la decisión y que la decisión es del médico tratante."],
  ];
  puntos.forEach(([tit, txt], i) => {
    const y = 1.8 + i * 1.16;
    tarjeta(s, 5.14, y, 7.6, 1.02);
    s.addText(tit, {
      x: 5.4, y: y + 0.12, w: 7.1, h: 0.3,
      fontFace: CUERPO, fontSize: 12.5, bold: true, color: C.petroleo,
      margin: 0, isTextBox: true,
    });
    s.addText(txt, {
      x: 5.4, y: y + 0.42, w: 7.1, h: 0.52,
      fontFace: CUERPO, fontSize: 11, color: C.tintaSuave,
      lineSpacingMultiple: 1.16, margin: 0, isTextBox: true,
    });
  });

  tarjeta(s, M, 6.5, ANCHO, 0.62, { fondo: C.ambarSuave, borde: "E8D5AC" });
  s.addText(
    "Advertencia: el modelo desplegado se entrenó con un conjunto de demostración simulado. Sus cifras ilustran el funcionamiento del componente y no son un hallazgo de la investigación.",
    {
      x: M + 0.28, y: 6.6, w: ANCHO - 0.56, h: 0.42,
      fontFace: CUERPO, fontSize: 11.5, bold: true, color: C.ambar,
      margin: 0, isTextBox: true,
    },
  );

  s.addNotes(
    "El tiempo de inferencia se sitúa en el orden de 13 milisegundos frente a la " +
    "meta de dos segundos del RNF02. Los resultados del OE3 saldrán de ejecutar " +
    "la comparación sobre el dataset real.",
  );
}

// ===========================================================================
// 12 · Evidencia de calidad
// ===========================================================================
{
  const s = lamina(
    "Lo que sostiene cada afirmación",
    "115 pruebas automatizadas y un registro de incidencias con causa raíz y forma de detección.",
  );

  const cifras = [
    ["115", "pruebas en verde", "79 en el API · 36 en la app", C.verde],
    ["13", "incidencias registradas", "todas cerradas, con causa raíz", C.coral],
    ["0", "defectos abiertos", "ninguno llegó al usuario", C.azul],
  ];
  cifras.forEach(([n, t, sub, color], i) => {
    const x = M + i * 2.28;
    tarjeta(s, x, 1.78, 2.06, 2.0);
    s.addText(n, {
      x: x + 0.16, y: 1.9, w: 1.74, h: 0.72,
      fontFace: TITULO, fontSize: 40, bold: true, color,
      align: "center", margin: 0, isTextBox: true,
    });
    s.addText(t, {
      x: x + 0.1, y: 2.64, w: 1.86, h: 0.5,
      fontFace: CUERPO, fontSize: 11.5, bold: true, color: C.petroleo,
      align: "center", lineSpacingMultiple: 1.05, margin: 0, isTextBox: true,
    });
    s.addText(sub, {
      x: x + 0.1, y: 3.16, w: 1.86, h: 0.5,
      fontFace: CUERPO, fontSize: 9.5, color: C.tintaSuave,
      align: "center", lineSpacingMultiple: 1.12, margin: 0, isTextBox: true,
    });
  });

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "Incidencias registradas", labels: ["Sprint 1", "Sprint 2", "Sprint 3"], values: [1, 6, 6] },
      { name: "Detectadas por prueba o verificación", labels: ["Sprint 1", "Sprint 2", "Sprint 3"], values: [0, 5, 6] },
    ],
    {
      x: 7.3, y: 1.72, w: 5.42, h: 3.0,
      barDir: "col",
      showTitle: true,
      title: "Incidencias por sprint y cómo se detectaron",
      titleFontFace: CUERPO, titleFontSize: 12, titleColor: C.petroleo,
      chartColors: [C.coral, C.verde],
      showValue: true,
      dataLabelPosition: "outEnd",
      dataLabelFontFace: CUERPO, dataLabelFontSize: 10, dataLabelColor: C.tinta,
      catAxisLabelFontFace: CUERPO, catAxisLabelFontSize: 10, catAxisLabelColor: C.tintaSuave,
      valAxisLabelFontFace: CUERPO, valAxisLabelFontSize: 9, valAxisLabelColor: C.tintaSuave,
      valAxisMaxVal: 8,
      valGridLine: { color: "E4EAF0", size: 1 },
      catGridLine: { style: "none" },
      showLegend: true, legendPos: "b",
      legendFontFace: CUERPO, legendFontSize: 10, legendColor: C.tintaSuave,
    },
  );

  tarjeta(s, M, 4.02, 6.62, 2.33, { fondo: C.azulClaro, borde: "BBD3E4" });
  s.addText("Cómo se lee este indicador", {
    x: M + 0.3, y: 4.18, w: 6.0, h: 0.34,
    fontFace: TITULO, fontSize: 15, bold: true, color: C.petroleo,
    margin: 0, isTextBox: true,
  });
  s.addText(
    "La densidad de defectos no baja entre el Sprint 2 y el Sprint 3, y sería deshonesto presentarla como si lo hiciera: ambos incorporaron componentes nuevos, y el defecto se concentra en lo que se escribe por primera vez.",
    {
      x: M + 0.3, y: 4.58, w: 6.05, h: 1.02,
      fontFace: CUERPO, fontSize: 12, color: C.tinta,
      lineSpacingMultiple: 1.22, margin: 0, isTextBox: true,
    },
  );
  s.addText(
    "Lo que sí mejoró es la forma de detección: de cinco de seis a seis de seis por prueba o verificación dirigida.",
    {
      x: M + 0.3, y: 5.64, w: 6.05, h: 0.6,
      fontFace: CUERPO, fontSize: 12, bold: true, color: C.azul,
      lineSpacingMultiple: 1.22, margin: 0, isTextBox: true,
    },
  );

  tarjeta(s, 7.3, 4.92, 5.42, 1.43, { fondo: C.verdeSuave, borde: "BFDECD" });
  s.addText(
    "Las pruebas no verifican solo que el sistema haga lo que debe, sino que no haga lo que no debe: un médico ajeno no accede a la ficha, un paciente no registra tomas por otro, un familiar no corrobora fuera de plazo.",
    {
      x: 7.56, y: 5.08, w: 4.9, h: 1.12,
      fontFace: CUERPO, fontSize: 11.5, color: C.tinta,
      lineSpacingMultiple: 1.22, margin: 0, isTextBox: true,
    },
  );

  s.addNotes(
    "Once de las trece incidencias las encontró una prueba automatizada o una " +
    "verificación dirigida. Ninguna llegó al usuario.",
  );
}

// ===========================================================================
// 13 · Objetivos
// ===========================================================================
{
  const s = lamina(
    "Estado de los objetivos específicos",
    "Avance al corte de la semana 4, con la evidencia que respalda cada uno.",
  );

  const oes = [
    ["OE1", "Caracterizar el proceso actual y sus factores", 100, "Cumplido", C.verde, "Entrevista aplicada · 4 brechas · 5 dimensiones OMS"],
    ["OE2", "Determinar los requisitos del sistema", 100, "Cumplido", C.verde, "10 requisitos funcionales · 6 no funcionales con ISO/IEC 25010"],
    ["OE3", "Determinar el algoritmo más predictivo", 70, "En ejecución", C.coral, "Protocolo implementado y modelo integrado · falta el dataset real"],
    ["OE4", "Construir el sistema de soporte clínico", 70, "En ejecución", C.coral, "7 de 10 requisitos operativos y desplegados"],
    ["OE5", "Evaluar la usabilidad con la escala SUS", 0, "Programado", C.tintaTenue, "Instrumento formalizado · aplicación en la semana 7"],
  ];

  oes.forEach(([cod, nom, pct, est, color, ev], i) => {
    const y = 1.75 + i * 1.02;
    tarjeta(s, M, y, ANCHO, 0.9);
    distintivo(s, cod, M + 0.18, y + 0.2, { diametro: 0.5, tamano: 9.5, fondo: C.petroleo });
    s.addText(nom, {
      x: M + 0.8, y: y + 0.13, w: 5.65, h: 0.32,
      fontFace: CUERPO, fontSize: 12.5, bold: true, color: C.petroleo,
      margin: 0, isTextBox: true,
    });
    s.addText(ev, {
      x: M + 0.8, y: y + 0.45, w: 5.6, h: 0.32,
      fontFace: CUERPO, fontSize: 10.5, color: C.tintaSuave,
      margin: 0, isTextBox: true,
    });

    s.addShape(pres.ShapeType.rect, {
      x: M + 6.6, y: y + 0.38, w: 3.5, h: 0.16,
      fill: { color: "E4EAF0" }, line: { width: 0 },
    });
    if (pct > 0) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 6.6, y: y + 0.38, w: (3.5 * pct) / 100, h: 0.16,
        fill: { color }, line: { width: 0 },
      });
    }
    s.addText(pct + " %", {
      x: M + 10.2, y: y + 0.28, w: 0.7, h: 0.34,
      fontFace: CUERPO, fontSize: 12, bold: true, color: C.petroleo,
      align: "right", margin: 0, isTextBox: true,
    });
    s.addText(est, {
      x: M + 11.0, y: y + 0.28, w: 1.05, h: 0.34,
      fontFace: CUERPO, fontSize: 10.5, bold: true, color,
      align: "right", margin: 0, isTextBox: true,
    });
  });

  pie(s, "OE3 y OE5 dependen de trabajo de campo en curso: la extracción documental del Anexo n.º 04 y las pruebas con usuarios de la semana 7.");
  s.addNotes(
    "OE3 está al 70 % porque el protocolo experimental está implementado y " +
    "verificado, y el modelo integrado en el sistema. Lo que falta es el " +
    "insumo, no el método.",
  );
}

// ===========================================================================
// 14 · Cierre
// ===========================================================================
{
  const s = laminaOscura();

  s.addText("Al corte del 50 %", {
    x: M, y: 0.72, w: ANCHO, h: 0.6,
    fontFace: TITULO, fontSize: 32, bold: true, color: C.blanco,
    margin: 0, isTextBox: true,
  });
  s.addText(
    "El escenario funcional está completo, verificado y desplegado. Lo que falta tiene fecha y sprint asignados.",
    {
      x: M, y: 1.34, w: 11.0, h: 0.56,
      fontFace: CUERPO, fontSize: 14, color: C.azulClaro,
      margin: 0, isTextBox: true,
    },
  );

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 2.1, w: 6.0, h: 3.7, rectRadius: 0.06,
    fill: { color: C.petroleoAlt }, line: { color: "2C5670", width: 1 },
  });
  s.addText("ENTREGADO", {
    x: M + 0.36, y: 2.34, w: 3.0, h: 0.3,
    fontFace: CUERPO, fontSize: 11, bold: true, color: C.verde,
    charSpacing: 1.2, margin: 0, isTextBox: true,
  });
  s.addText(
    [
      { text: "Acceso por perfil y gestión del paciente polimedicado", options: { bullet: true, breakLine: true } },
      { text: "Registro de la toma sin conexión y sincronización idempotente", options: { bullet: true, breakLine: true } },
      { text: "Predicción del riesgo integrada en la ficha clínica", options: { bullet: true, breakLine: true } },
      { text: "Alertas de toma programadas en el dispositivo", options: { bullet: true, breakLine: true } },
      { text: "Corroboración de la toma por el grupo familiar", options: { bullet: true, breakLine: true } },
      { text: "Restablecimiento de la contraseña por correo", options: { bullet: true } },
    ],
    {
      x: M + 0.36, y: 2.76, w: 5.3, h: 2.86,
      fontFace: CUERPO, fontSize: 13, color: C.blanco,
      lineSpacingMultiple: 1.16, paraSpaceAfter: 8, margin: 0, isTextBox: true,
    },
  );

  s.addShape(pres.ShapeType.roundRect, {
    x: 7.05, y: 2.1, w: 5.68, h: 3.7, rectRadius: 0.06,
    fill: { color: C.petroleoAlt }, line: { color: "2C5670", width: 1 },
  });
  s.addText("PENDIENTE", {
    x: 7.41, y: 2.34, w: 3.0, h: 0.3,
    fontFace: CUERPO, fontSize: 11, bold: true, color: C.coral,
    charSpacing: 1.2, margin: 0, isTextBox: true,
  });

  const pendiente = [
    ["Alertas tempranas al médico", "RF05 · Sprint 3"],
    ["Explicabilidad individual con SHAP", "RF06 · Sprint 3"],
    ["Exportación de reportes del panel", "RF07 · Sprint 3"],
    ["Comparación sobre el dataset real", "OE3 · extracción en curso"],
    ["Validación de usabilidad con SUS", "OE5 · Sprint 4"],
  ];
  pendiente.forEach(([tit, ref], i) => {
    const y = 2.8 + i * 0.58;
    s.addText(tit, {
      x: 7.41, y, w: 3.5, h: 0.32,
      fontFace: CUERPO, fontSize: 12.5, color: C.blanco,
      margin: 0, isTextBox: true,
    });
    s.addText(ref, {
      x: 10.9, y, w: 1.65, h: 0.32,
      fontFace: CUERPO, fontSize: 10.5, color: C.tintaTenue,
      align: "right", margin: 0, isTextBox: true,
    });
  });

  s.addText(
    "Gracias.  ·  Leonardo Jesús Guzmán Salazar  ·  Seminario de Tesis I  ·  USAT 2026-II",
    {
      x: M, y: 6.32, w: ANCHO, h: 0.4,
      fontFace: CUERPO, fontSize: 12, color: C.azulClaro,
      margin: 0, isTextBox: true,
    },
  );

  s.addNotes(
    "Cerrar declarando el alcance con precisión: la rúbrica premia que el " +
    "escenario esté completo y verificado, no que todo el sistema esté " +
    "terminado.",
  );
}

pres
  .writeFile({ fileName: "Exposicion_50.pptx" })
  .then((f) => console.log("Generado:", f))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });
