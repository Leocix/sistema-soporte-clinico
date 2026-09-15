# App del paciente — CDSS Adherencia

Aplicación Flutter del paciente polimedicado y de su acompañante familiar.
Cubre RF01 (acceso con perfil de paciente o familiar), RF03 (registro de la toma
con sincronización sin conexión), RF08 (recordatorios de toma), RF09
(corroboración por el grupo familiar) y RF10 (recuperación de la contraseña).

Verificado con **Flutter 3.47.2**: `flutter analyze` sin incidencias, **40
pruebas en verde** y **APK de publicación** instalado y probado en un
dispositivo Android real.

## Puesta en marcha

### 1. Antes de nada: crear la cuenta del paciente

La ficha clínica y la cuenta de acceso son entidades distintas. Sin cuenta no
hay con qué iniciar sesión, así que la carga inicial la crea:

```bash
python scripts/seed.py --demo
```

Imprime los correos de acceso (`d-001@ejemplo.pe` … `d-005@ejemplo.pe`), con la
misma contraseña que definiste en `SEED_PASSWORD`.

### 2. Instalar dependencias y ejecutar

```bash
flutter pub get
```

```bash
flutter run
```

La aplicación apunta por defecto al API en producción. Para trabajar contra el
backend local:

```bash
flutter run --dart-define=API_URL=http://10.0.2.2:8000
```

`10.0.2.2` es la dirección con la que el emulador de Android alcanza al PC;
`localhost` apuntaría al propio emulador. En un dispositivo físico usa la IP
del equipo en la red local.

### 3. Pruebas

```bash
flutter test
```

14 casos: validación del formulario de acceso, contrato con el API (cuerpo
enviado, traducción de errores, distinción entre fallo de red y error de
negocio) y la lógica de estado de la toma.

Para ejecutar en Android hacen falta las licencias del SDK, que `flutter
doctor` reporta como pendientes:

```bash
flutter doctor --android-licenses
```

## Instalar en un teléfono Android

Para la sustentación o para entregársela a un paciente, lo práctico es el APK
en lugar del cable:

```bash
flutter build apk --release
```

Queda en `build/app/outputs/flutter-apk/app-release.apk` (~52 MB) y una copia
lista para compartir en `entregable/cdss-adherencia.apk`.

Pásalo al teléfono por cable, correo o nube, ábrelo desde el gestor de archivos
y acepta **«Instalar aplicaciones desconocidas»** cuando Android lo pida: es lo
normal para un APK que no viene de Play Store.

El APK apunta al API en producción, así que **funciona sin el PC encendido**.
Para que apunte a un servidor distinto hay que recompilar:

```bash
flutter build apk --release --dart-define=API_URL=https://otro-servidor
```

## Cómo funciona

### Sin conexión

El paciente puede estar sin cobertura justo cuando toma su medicación, así que
la aplicación **nunca bloquea la confirmación**: guarda el evento en una cola
local (`shared_preferences`) y lo envía cuando puede, en un solo lote a
`POST /api/adherencia/registros/lote`.

Reintentar es seguro porque el servidor identifica cada evento por la terna
(paciente, medicamento, horario programado): un envío repetido actualiza el
registro existente en lugar de duplicarlo. Sin esa garantía, los reintentos
inflarían la tasa de adherencia y contaminarían las características del modelo
predictivo.

### El estado de la toma no lo elige el paciente

El paciente confirma que tomó la dosis; la aplicación decide si fue puntual o
con retraso comparando la hora real con la prescrita (margen de 30 minutos).
Pedirle que se autocalifique sería devolverle el autorreporte subjetivo que el
sistema pretende sustituir.

### Los recordatorios se programan en el teléfono (RF08)

Responde a la brecha B4 del diagnóstico: el olvido es la primera causa de
incumplimiento que refirió el médico. Los avisos **no se envían desde el
servidor**, se programan en el dispositivo. Es lo que corresponde a un paciente
que puede estar sin cobertura justo a la hora de su medicación: un recordatorio
que dependiera de la red fallaría precisamente en el escenario que más lo
necesita.

El permiso se pide cuando el paciente configura su plan y entiende para qué
sirve, no al arrancar. Los avisos se reprograman con cada cambio del plan —un
aviso de un medicamento retirado le diría que tome algo que ya no toma— y se
restauran tras reiniciar el teléfono.

Se usa programación inexacta a propósito: la exacta requiere un permiso que
Android reserva para relojes y calendarios, y para un recordatorio de
medicación un margen de minutos es aceptable.

### El plan de tomas vive en el teléfono

El modelo de datos actual guarda la carga terapéutica de forma agregada
—número de fármacos y tomas al día—, no la lista nominal de prescripciones.
Mientras el médico no gestione el esquema farmacológico desde el panel
(Sprint 3), el paciente declara su plan en la app y lo que se sincroniza con el
servidor son los eventos de toma, que es lo que alimenta el cálculo de
adherencia.

## Estructura

```
lib/
├── main.dart                    # Arranque y rehidratación de la sesión
├── models/
│   ├── sesion.dart              # Usuario y ficha del paciente
│   ├── medicamento.dart         # Plan local de tomas
│   ├── toma.dart                # Evento de adherencia y dosis del día
│   └── resumen_adherencia.dart  # Indicadores en lenguaje llano
├── screens/
│   ├── login_screen.dart        # RF01
│   ├── home_screen.dart         # Tomas de hoy y cumplimiento
│   ├── registro_toma.dart       # RF03: dosis no tomada y su motivo
│   └── plan_screen.dart         # Medicamentos y horarios
├── services/
│   ├── api_service.dart         # Cliente HTTP con JWT
│   ├── almacenamiento.dart      # Sesión, plan y cola pendiente
│   ├── sincronizacion.dart      # Envío tolerante a fallos de red
│   └── notification_service.dart# Recordatorios (RF08, Sprint 4)
├── utils/                       # Constantes y guía de estilo
└── widgets/                     # Tarjeta de toma y avisos
```

## Accesibilidad

El usuario objetivo es un adulto mayor polimedicado, así que las decisiones
visuales priorizan tamaño y contraste sobre densidad: texto base de 18 puntos,
áreas táctiles de 56 puntos de alto y dos botones literales por dosis. Es la
traducción concreta de RNF03, cuya meta es un puntaje SUS ≥ 80 que se medirá en
la semana 7 (OE5).

## Pendiente

- Ejecución en un dispositivo Android real (faltan las licencias del SDK).
