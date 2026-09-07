// Pruebas de widget de la aplicacion del paciente.
//
// Cubren el arranque y la validacion del formulario de acceso (RF01). No
// tocan la red: comprobar el registro de tomas contra el API es trabajo de
// las pruebas del backend, que ya verifican la idempotencia del envio.

import 'package:cdss_adherencia/main.dart';
import 'package:cdss_adherencia/models/sesion.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() {
    // Sin valores iniciales no hay sesion guardada: la aplicacion debe
    // terminar mostrando la pantalla de acceso.
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('sin sesion guardada se muestra la pantalla de acceso',
      (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    expect(find.text('Mi tratamiento'), findsOneWidget);
    expect(find.text('Ingresar'), findsOneWidget);
    expect(find.text('Correo electrónico'), findsOneWidget);
  });

  testWidgets('el formulario de acceso rechaza los campos vacios',
      (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Ingresar'));
    await tester.pump();

    expect(find.text('Escriba su correo.'), findsOneWidget);
    expect(find.text('Escriba su contraseña.'), findsOneWidget);
  });

  testWidgets('un correo sin arroba no supera la validacion', (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextFormField).first, 'correo-invalido');
    await tester.tap(find.text('Ingresar'));
    await tester.pump();

    expect(find.text('El correo no parece válido.'), findsOneWidget);
  });

  testWidgets('el acceso deja elegir entre paciente y familiar',
      (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    final selector = find.byType(SegmentedButton<PerfilUsuario>);
    expect(selector, findsOneWidget);
    expect(find.text('Soy el paciente'), findsOneWidget);
    expect(find.text('Soy familiar'), findsOneWidget);

    // Entra como paciente mientras no se toque nada: es el caso mayoritario y
    // el usuario que menos debe tener que configurar.
    SegmentedButton<PerfilUsuario> leer() =>
        tester.widget(selector) as SegmentedButton<PerfilUsuario>;
    expect(leer().selected, {PerfilUsuario.paciente});

    await tester.tap(find.text('Soy familiar'));
    await tester.pumpAndSettle();
    expect(leer().selected, {PerfilUsuario.familiar});
  });

  testWidgets('desde el acceso se llega al alta con código', (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    // El enlace queda al pie de un formulario que puede desbordar la
    // pantalla: hay que traerlo a la vista antes de pulsarlo.
    await tester.ensureVisible(find.text('Un familiar me dio un código'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Un familiar me dio un código'));
    await tester.pumpAndSettle();

    expect(find.text('Crear mi cuenta'), findsWidgets);
    expect(find.text('Código'), findsOneWidget);
  });

  testWidgets('el alta con código exige el código completo', (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    // El enlace queda al pie de un formulario que puede desbordar la
    // pantalla: hay que traerlo a la vista antes de pulsarlo.
    await tester.ensureVisible(find.text('Un familiar me dio un código'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Un familiar me dio un código'));
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextFormField).first, 'ABC');

    final boton = find.widgetWithText(FilledButton, 'Crear mi cuenta');
    await tester.ensureVisible(boton);
    await tester.pumpAndSettle();
    await tester.tap(boton);
    await tester.pump();

    expect(find.text('Escriba el código completo.'), findsOneWidget);
  });
}
